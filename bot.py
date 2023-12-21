import codecs
import aiogram
from quiz import *
from user_progress import *
from chat_data import *
from text import *
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

# TOKEN = str(os.getenv('TOKEN'))
TOKEN = str(os.getenv('TOKEN_TEST'))

# Инициализация бота и диспетчера
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

# users_progress_weights = load_json_file('users_progress.json', None)
users_progress_weights_en = load_json_file('users_progress_en.json', None)
users_progress_weights_ru = load_json_file('users_progress_ru.json', None)
questions = load_json_file('questions.json', None)
messages = load_json_file('messages.json', list)

# Main word data storage
ru_list, en_list, ru_list_long, en_list_long = create_lists()
ru_word_dict, en_word_dict, ru_dict_ind, en_dict_ind, ru_word_dict_long, en_word_dict_long \
    = create_word_dicts(ru_list=ru_list, en_list=en_list, ru_list_long=ru_list_long, en_list_long=en_list_long)
ru_word_dict_numbers, en_word_dict_numbers = create_embedding_dicts(ru_word_dict=ru_word_dict,
                                                                    en_word_dict=en_word_dict)
ru_string_search = StringSearch(ru_list)
en_string_search = StringSearch(en_list)

actualise_user_progress(ru_list=ru_list, en_list=en_list, users_progress_weights_en=users_progress_weights_en,
                        users_progress_weights_ru=users_progress_weights_ru)


async def main() -> None:
    """Initiate the bot"""
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start(message: types.Message) -> None:
    """React to the Start command"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    await initiate_user_progress(user_id=user_id, en_list=en_list, ru_list=ru_list,
                                 users_progress_weights_en=users_progress_weights_en,
                                 users_progress_weights_ru=users_progress_weights_ru)
    initial_message = await bot.send_message(chat_id=chat_id,
                                             text="Плотный салам")
    messages[message.chat.id].append(initial_message.message_id)
    await send_instructions(message)
    messages[chat_id].append(message.message_id)

    await save_user_messages(messages=messages)


@dp.message(aiogram.filters.command.Command(commands='spin'))
async def spin(message: types.Message) -> None:
    """React to the Spin command"""
    chat_id = message.chat.id
    user_id = message.from_user.id

    await initiate_user_progress(user_id=user_id, en_list=en_list, ru_list=ru_list,
                                 users_progress_weights_en=users_progress_weights_en,
                                 users_progress_weights_ru=users_progress_weights_ru)

    # Searching for a new question
    question, answer, question_language = await choose_question(user_id=user_id,
                                                                users_progress_weights_ru=users_progress_weights_ru,
                                                                users_progress_weights_en=users_progress_weights_en,
                                                                ru_word_dict=ru_word_dict,
                                                                en_word_dict=en_word_dict)

    # Preparing new options
    questions[chat_id] = (question, question_language)
    await save_user_questions(questions=questions)

    builder = await inline_builder(question=question, question_language=question_language, ru_word_dict=ru_word_dict,
                                   en_word_dict=en_word_dict)

    # Sending new message
    game_message = await message.answer("Как переводится:\n\n"
                                        f"{question}",
                                        reply_markup=builder.as_markup())

    messages[chat_id].append(game_message.message_id)
    messages[chat_id].append(message.message_id)

    await save_user_messages(messages=messages)


@dp.message(aiogram.filters.command.Command(commands='save'))
async def save_progress(message: types.Message) -> None:
    """React to the Save command"""
    await save_user_progress('russian', users_progress_weights_en=users_progress_weights_en,
                             users_progress_weights_ru=users_progress_weights_ru)
    await save_user_progress('english', users_progress_weights_en=users_progress_weights_en,
                             users_progress_weights_ru=users_progress_weights_ru)

    chat_id = message.chat.id
    messages[chat_id].append(message.message_id)

    await save_user_messages(messages=messages)


@dp.message(aiogram.filters.command.Command(commands='instruct'))
async def send_instructions(message: types.Message) -> None:
    """React to the Instruct command"""
    chat_id = message.chat.id
    text = """
1. Для вызова игры в меню используйте функцию 'Крути барабан', которая запустит игру с выбором правильного перевода слова. Вам могут выпадать сообщения с идиомами после прокрутки барабана

2. Чат сохраняет ваш прогресс. Отвечаете правильно - этот вопрос будет попадаться все меньше, и наоборот

3. Если вы напишете сообщение в чат вам вернется найденное слово и его перевод на основе вашего сообщения. Рекомендую потестировать, написав пару неполных слов
"""
    await bot.send_message(chat_id=message.chat.id,
                           text=text)
    messages[chat_id].append(message.message_id)

    await save_user_messages(messages=messages)


@dp.message()
async def find_translation(message: types.message) -> None:
    """React to a user message"""
    chat_id = message.chat.id

    found_word, found_translation = await find_word(query=message.text,
                                                    ru_word_dict=ru_word_dict,
                                                    en_word_dict=en_word_dict,
                                                    ru_word_dict_numbers=ru_word_dict_numbers,
                                                    en_word_dict_numbers=en_word_dict_numbers)

    found_word_hash, found_translation_hash = await find_word_hash(query=message.text,
                                                                   ru_word_dict=ru_word_dict,
                                                                   en_word_dict=en_word_dict,
                                                                   ru_string_search=ru_string_search,
                                                                   en_string_search=en_string_search)
    if found_word is None:
        find_message = await bot.send_message(chat_id=chat_id,
                                              text=f"Ошибочка вышла:\n\nНе смог найти")
        messages[chat_id].append(find_message)
    elif (found_word == found_word_hash) or (found_word_hash is None):
        await bot.send_message(chat_id=message.chat.id,
                               text=f"Ты это искал:\n\nФраза: {found_word}\n\nПеревод: {found_translation}")
    else:
        await bot.send_message(chat_id=chat_id,
                               text=f"Для тебя есть два варианта:"
                                    f"\n\nФраза: {found_word}\n\nПеревод: {found_translation}\n\n"
                                    f"Фраза: {found_word_hash}\n\nПеревод: {found_translation_hash}")


async def send_extra_info(chat_id: int) -> None:
    """Send message with long question"""
    question, answer, question_language = await choose_extra_info(en_word_dict_long=en_word_dict_long,
                                                                  ru_word_dict_long=ru_word_dict_long)
    extra_info_message = await bot.send_message(chat_id=chat_id,
                                                text=f"Глянь важную инфу\n\nФраза: {question}\n\nПеревод: {answer}")

    messages[chat_id].append(extra_info_message.message_id)


@dp.callback_query()
async def check_translation(callback_query: types.callback_query) -> None:
    """Check user's answer"""
    user_translation = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    question, question_language = questions[chat_id]

    if question_language == 'russian':
        correct_translation = ru_word_dict[question]
    else:
        correct_translation = en_word_dict[question]

    if user_translation == correct_translation:
        # Deleting previous messages
        for message_id in messages.get(chat_id, None):
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                continue

        messages[chat_id] = []

        await update_user_progress(user_id=user_id,
                                   question_language=question_language,
                                   question=question,
                                   answer_status='right',
                                   users_progress_weights_ru=users_progress_weights_ru,
                                   users_progress_weights_en=users_progress_weights_en)

        await save_user_progress(question_language=question_language,
                                 users_progress_weights_ru=users_progress_weights_ru,
                                 users_progress_weights_en=users_progress_weights_en)

        # Searching for a new question
        # Make it more efficient by splitting the dataset by the length
        question, answer, question_language = await choose_question(user_id=user_id,
                                                                    users_progress_weights_ru=users_progress_weights_ru,
                                                                    users_progress_weights_en=users_progress_weights_en,
                                                                    ru_word_dict=ru_word_dict,
                                                                    en_word_dict=en_word_dict)

        greet_message = await bot.send_message(chat_id=chat_id,
                                               text=f"Правильно, Валерий Игоревич оценил")
        messages[chat_id].append(greet_message.message_id)

        await send_extra_info(chat_id=chat_id)

        new_question = f"Как переводится:\n\n{question}"

        # Preparing new buttons
        questions[chat_id] = (question, question_language)
        await save_user_questions(questions=questions)

        builder = await inline_builder(question=question, question_language=question_language,
                                       ru_word_dict=ru_word_dict,
                                       en_word_dict=en_word_dict)

        # Sending new markup
        new_question_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=new_question,
                                                      reply_markup=builder.as_markup())
        messages[chat_id].append(new_question_message.message_id)

        await save_user_messages(messages=messages)

    else:
        # Wrong answer message
        wrong_answer_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=f"Неверно. Не разочаровывай, выбери еще раз")
        await update_user_progress(user_id=user_id,
                                   question_language=question_language,
                                   question=question,
                                   answer_status='right',
                                   users_progress_weights_ru=users_progress_weights_ru,
                                   users_progress_weights_en=users_progress_weights_en)

        await save_user_progress(question_language=question_language,
                                 users_progress_weights_ru=users_progress_weights_ru,
                                 users_progress_weights_en=users_progress_weights_en)

        messages[chat_id].append(wrong_answer_message.message_id)

        await save_user_messages(messages=messages)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG,
                        format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')
    asyncio.run(main())
