import codecs
import json
import os
import random
import aiofiles
import aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from english_words import *
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from collections import defaultdict

# TOKEN = str(os.getenv('TOKEN'))
TOKEN = str(os.getenv('TOKEN_TEST'))

# Инициализация бота и диспетчера
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

# Main bot storage
questions = defaultdict()
messages = defaultdict(list)
unique_users = set()

if 'users_progress.json' in os.listdir():
    with open('users_progress.json', 'r') as file:
        data = json.load(file, object_hook=lambda x: {int(k) if k.isdigit() else k: v for k, v in x.items()})
    users_progress_weights = defaultdict(None, data)
else:
    users_progress_weights = defaultdict()

# Main data storage
ru_list, en_list = create_lists()
ru_word_dict, en_word_dict, ru_dict_ind, en_dict_ind = create_word_dicts(ru_list=ru_list, en_list=en_list)
ru_word_dict_numbers, en_word_dict_numbers = create_embedding_dicts(ru_word_dict=ru_word_dict,
                                                                    en_word_dict=en_word_dict)
ru_string_search = StringSearch(ru_list)
en_string_search = StringSearch(en_list)


async def choose_question(user_id):
    choice = random.randint(0, 1)

    if choice == 0:
        question = random.choices(ru_list, weights=users_progress_weights[user_id], k=1)[0]
        translation = ru_word_dict.get(question)
        language = 'russian'
    else:
        question = random.choices(en_list, weights=users_progress_weights[user_id], k=1)[0]
        translation = en_word_dict.get(question)
        language = 'english'

    if len(question.encode('utf-8')) < 62 and len(translation.encode('utf-8')) < 62:
        return question, translation, language, 'short'
    else:
        return question, translation, language, 'long'


async def choose_options(question: str, question_language: str) -> list[str]:
    def get_random_word(language):
        word_list = en_list if language == 'russian' else ru_list
        return random.choice(word_list)

    options = []

    while len(options) < 3:
        option = get_random_word(question_language)
        if len(option.encode('utf-8')) < 62:
            options.append(option)

    word_dict = ru_word_dict if question_language == 'russian' else en_word_dict
    options.append(word_dict[question])

    random.shuffle(options)
    return options


async def save_number_users(file_path, content):
    try:
        async with aiofiles.open(file_path, 'w') as file:
            await file.write(content)
        print(f"Content saved to {file_path} asynchronously.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def initiate_user_progress(user_id):
    if user_id not in users_progress_weights.keys():
        users_progress_weights[user_id] = [1 for _ in range(len(ru_list))]
    else:
        if len(ru_list) > len(users_progress_weights[user_id]):
            users_progress_weights[user_id] += [2] * (len(ru_list) - len(users_progress_weights[user_id]))


async def update_user_progress(user_id, question, language, answer_status):
    if user_id in users_progress_weights.keys():
        if language == 'russian':
            question_index = ru_dict_ind[question]
        elif language == 'english':
            question_index = en_dict_ind[question]

        if answer_status == 'right':
            coefficient = 0.5
        elif answer_status == 'wrong':
            coefficient = 2

        users_progress_weights[user_id][question_index] = round(
            users_progress_weights[user_id][question_index] * coefficient, 4)


async def save_user_progress():
    async with aiofiles.open('users_progress.json', 'w') as file:
        await file.write(json.dumps(users_progress_weights))


async def inline_builder(question, question_language):
    options = await choose_options(question=question, question_language=question_language)

    # Preparing new buttons
    buttons = []
    for option in options:
        buttons.append(InlineKeyboardButton(text=option, callback_data=option))

    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    builder = InlineKeyboardBuilder.from_markup(markup)

    builder.adjust(1, 1, 1, 1)

    return builder


async def main() -> None:
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    unique_users.add(user_id)
    await initiate_user_progress(user_id)
    await save_number_users(file_path='unique_users.txt', content=f'{len(unique_users)}')
    initial_message = await bot.send_message(chat_id=chat_id,
                                             text="Плотный салам")
    messages[message.chat.id].append(initial_message.message_id)
    await send_instructions(message)
    messages[chat_id].append(message.message_id)


@dp.message(aiogram.filters.command.Command(commands='spin'))
async def spin(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    unique_users.add(user_id)
    await initiate_user_progress(user_id)

    # Searching for a new question
    question, answer, question_language, question_status = await choose_question(user_id=user_id)
    if question_status == 'long':
        while question_status == 'long':
            question, answer, question_language, question_status = await choose_question(user_id=user_id)

    # Preparing new options
    questions[chat_id] = (question, question_language)
    builder = await inline_builder(question=question, question_language=question_language)

    # Sending new message
    game_message = await message.answer("Как переводится:\n\n"
                                        f"{question}",
                                        reply_markup=builder.as_markup())

    messages[chat_id].append(game_message.message_id)
    messages[chat_id].append(message.message_id)


@dp.message(aiogram.filters.command.Command(commands='save'))
async def save_progress(message: types.Message):
    await save_user_progress()
    chat_id = message.chat.id
    messages[chat_id].append(message.message_id)


@dp.message(aiogram.filters.command.Command(commands='instruct'))
async def send_instructions(message: types.Message):
    chat_id = message.chat.id
    text = """
1. Для вызова игры в меню используйте функцию 'Крути барабан', которая запустит игру с выбором правильного перевода слова. Вам могут выпадать сообщения с идиомами после прокрутки барабана

2. Чат сохраняет ваш прогресс. Отвечаете правильно - этот вопрос будет попадаться все меньше, и наоборот

3. Если вы напишете сообщение в чат вам вернется найденное слово и его перевод на основе вашего сообщения. Рекомендую потестировать, написав пару неполных слов
"""
    instruction_message = await bot.send_message(chat_id=message.chat.id,
                                                 text=text)
    messages[chat_id].append(instruction_message.message_id)
    messages[chat_id].append(message.message_id)


@dp.message()
async def find_translation(message: types.message):
    unique_users.add(message.from_user.id)
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
        find_message = await bot.send_message(chat_id=message.chat.id,
                                              text=f"Ошибочка вышла:\n\nНе смог найти")
    elif (found_word == found_word_hash) or (found_word_hash is None):
        find_message = await bot.send_message(chat_id=message.chat.id,
                                              text=f"Ты это искал:\n\nФраза: {found_word}\n\nПеревод: {found_translation}")
    else:
        find_message = await bot.send_message(chat_id=message.chat.id,
                                              text=f"Для тебя есть два варианта:"
                                                   f"\n\nФраза: {found_word}\n\nПеревод: {found_translation}\n\n"
                                                   f"Фраза: {found_word_hash}\n\nПеревод: {found_translation_hash}")

    messages[chat_id].append(find_message.message_id)
    messages[chat_id].append(message.message_id)


@dp.callback_query()
async def check_translation(callback_query: types.callback_query):
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
            except:
                continue
        messages[chat_id] = []

        await update_user_progress(user_id=user_id,
                                   language=question_language,
                                   question=question,
                                   answer_status='right')
        await save_user_progress()

        # Searching for a new question
        # Make it more efficient by splitting the dataset by the length
        question, answer, question_language, question_status = await choose_question(user_id=user_id)
        if question_status == 'long':
            greet_message = await bot.send_message(chat_id=chat_id,
                                                   text=f"Правильно, Валерий Игоревич оценил")
            messages[chat_id].append(greet_message.message_id)

            extra_info_message = await bot.send_message(chat_id=chat_id,
                                                        text=f"Глянь важную инфу\n\nФраза: {question}\n\nПеревод: {answer}")
            messages[chat_id].append(extra_info_message.message_id)

            while question_status == 'long':
                question, answer, question_language, question_status = await choose_question(user_id=user_id)

            new_question = f"Как переводится:\n\n{question}"
        else:
            new_question = f"Правильно, Валерий Игоревич оценил\n\nКак переводится:\n\n{question}"

        # Preparing new buttons
        questions[chat_id] = (question, question_language)
        builder = await inline_builder(question=question, question_language=question_language)

        # Sending new markup
        new_question_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=new_question,
                                                      reply_markup=builder.as_markup())
        messages[chat_id].append(new_question_message.message_id)
    else:
        # Wrong answer message
        wrong_answer_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=f"Неверно. Не разочаровывай, выбери еще раз")
        await update_user_progress(user_id=user_id,
                                   language=question_language,
                                   question=questions[chat_id][0],
                                   answer_status='wrong')
        await save_user_progress()
        messages[chat_id].append(wrong_answer_message.message_id)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG,
                        format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')
    asyncio.run(main())
