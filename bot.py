import codecs
import os
import random
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

TOKEN = str(os.getenv('TOKEN'))

# Инициализация бота и диспетчера
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

# Main bot storage
questions = defaultdict()
messages = defaultdict(list)
unique_users = set()

# Main data storage
ru_list, en_list = create_lists()
ru_word_dict, en_word_dict = create_word_dicts(ru_list=ru_list, en_list=en_list)
ru_word_dict_numbers, en_word_dict_numbers = create_embedding_dicts(ru_word_dict=ru_word_dict,
                                                                    en_word_dict=en_word_dict)


def choose_question():
    choice = random.randint(0, 1)
    if choice == 0:
        question = random.choice(ru_list)
        if len(question.encode('utf-8')) < 62 and ru_word_dict[question] is not None and len(
                ru_word_dict[question].encode('utf-8')) < 62:
            return question, None, 'russian'
        else:
            return question, ru_word_dict[question], 'russian'
    if choice == 1:
        question = random.choice(en_list)
        if len(question.encode('utf-8')) < 62 and en_word_dict[question] is not None and len(
                en_word_dict[question].encode('utf-8')) < 62:
            return question, None, 'english'
        else:
            return question, en_word_dict[question], 'english'


def choose_options(question: str, question_language: str) -> list[str]:
    options = []
    if question_language == 'russian':
        while len(options) < 3:
            option = random.choice(en_list)
            if len(option.encode('utf-8')) < 62:
                options.append(option)
        options.append(ru_word_dict[question])
    elif question_language == 'english':
        while len(options) < 3:
            option = random.choice(ru_list)
            if len(option.encode('utf-8')) < 62:
                options.append(option)
        options.append(en_word_dict[question])
    random.shuffle(options)
    return options


async def main() -> None:
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start(message: types.Message):
    unique_users.add(message.from_user.id)
    # Searching for a new question
    question, answer, question_language = choose_question()
    if answer is not None:
        while answer is not None:
            question, answer, question_language = choose_question()

    # Preparing new options
    questions[message.chat.id] = question
    options = choose_options(question=question, question_language=question_language)

    # Preparing new buttons
    buttons = []
    for option in options:
        buttons.append(InlineKeyboardButton(text=option, callback_data=option))

    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    builder = InlineKeyboardBuilder.from_markup(markup)

    builder.adjust(1, 1, 1, 1)

    # Sending new message
    initial_message = await bot.send_message(chat_id=message.chat.id,
                                          text="Плотный салам")
    game_message = await message.answer("Как переводится:\n\n"
                                           f"{question}",
                                           reply_markup=builder.as_markup())

    messages[message.chat.id].append(initial_message.message_id)
    messages[message.chat.id].append(game_message.message_id)

    with open('unique_users.txt', 'w') as file:
        file.write(f'{len(unique_users)}')


@dp.message(aiogram.filters.command.Command(commands='instruct'))
async def start(message: types.Message):
    unique_users.add(message.from_user.id)
    text = """
1. Для вызова игры в меню используйте функцию 'Крути_барабан', которая запустит игру с выбором правильного перевода слова. Вам могут выпадать сообщения с идиомами после прокрутки барабана.

2. Если вы напишете сообщение в чат вам вернется найденное слово и его перевод на основе вашего сообщения. Рекомендую потестировать, написав пару неполных слов.
"""
    instruction_message = await bot.send_message(chat_id=message.chat.id,
                                                 text=text)
    messages[message.chat.id].append(instruction_message.message_id)


@dp.message()
async def find_translation(message: types.message):
    unique_users.add(message.from_user.id)
    found_word, found_translation = find_word(query=message.text,
                                              ru_word_dict=ru_word_dict,
                                              en_word_dict=en_word_dict,
                                              ru_word_dict_numbers=ru_word_dict_numbers,
                                              en_word_dict_numbers=en_word_dict_numbers)
    if found_word is None:
        find_message = await bot.send_message(chat_id=message.chat.id,
                                              text=f"Ошибочка вышла:\n\nНе смог найти")
    else:
        find_message = await bot.send_message(chat_id=message.chat.id,
                                              text=f"Ты это искал:\n\n{found_word}\n\n{found_translation}")
    messages[message.chat.id].append(find_message.message_id)


@dp.callback_query(lambda callback_query: callback_query.data in en_list or callback_query.data in ru_list)
async def check_translation(callback_query: types.callback_query):
    unique_users.add(callback_query.from_user.id)
    user_translation = callback_query.data
    question_language = detect_text_language(questions[callback_query.message.chat.id])
    if question_language == 'russian':
        correct_translation = ru_word_dict[questions[callback_query.message.chat.id]]
    else:
        correct_translation = en_word_dict[questions[callback_query.message.chat.id]]

    if user_translation == correct_translation:

        # Deleting previous messages
        for message_id in messages[callback_query.message.chat.id]:
            try:
                await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_id)
            except:
                continue
        messages[callback_query.message.chat.id] = []

        # Searching for a new question
        question, answer, question_language = choose_question()
        if answer is not None:
            greet_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                   text=f"Правильно, Валерий Игоревич оценил")
            messages[callback_query.message.chat.id].append(greet_message.message_id)
            while answer is not None:
                extra_info_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                            text=f"Глянь важную инфу\n\nФраза: {question}\n\nПеревод: {answer}")
                messages[callback_query.message.chat.id].append(extra_info_message.message_id)
                question, answer, question_language = choose_question()

            new_question = f"Как переводится:\n\n{question}"
        else:
            new_question = f"Правильно, Валерий Игоревич оценил\n\nКак переводится:\n\n{question}"

        # Preparing new buttons
        questions[callback_query.message.chat.id] = question
        options = choose_options(question=question, question_language=question_language)

        buttons = []
        for option in options:
            buttons.append(InlineKeyboardButton(text=option, callback_data=option))

        markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
        builder = InlineKeyboardBuilder.from_markup(markup)
        builder.adjust(1, 1, 1, 1)

        # Sending new markup
        new_question_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=new_question,
                                                      reply_markup=builder.as_markup())
        messages[callback_query.message.chat.id].append(new_question_message.message_id)
    else:
        # Wrong answer message
        wrong_answer_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=f"Неверно. Не разочаровывай, выбери еще раз")
        messages[callback_query.message.chat.id].append(wrong_answer_message.message_id)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG,
                        format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')
    asyncio.run(main())
