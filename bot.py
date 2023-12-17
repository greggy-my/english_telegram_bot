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
from english_words import ru_list, en_list

# Создаем словарь с соответствиями слов и переводов
word_dict = defaultdict(lambda: None, zip(ru_list, en_list))

# Токен вашего бота, полученный от @BotFather
TOKEN = str(os.getenv('TOKEN'))

# Инициализация бота и диспетчера
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

questions = defaultdict()
messages = defaultdict(list)


def choose_question():
    question = random.choice(ru_list)
    if len(question.encode('utf-8')) >= 62 and len(word_dict[question].encode('utf-8')) >= 62:
        return question, word_dict[question]
    else:
        return question, None


def choose_options(question: str) -> list[str]:
    options = []
    while len(options) < 3:
        option = random.choice(en_list)
        if len(option.encode('utf-8')) < 62:
            options.append(option)
    options.append(word_dict[question])
    random.shuffle(options)
    return options


async def main() -> None:
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start(message: types.Message):

    # Searching for a new question
    question, answer = choose_question()
    if answer is not None:
        while answer is not None:
            question, answer = choose_question()

    # Preparing new options
    questions[message.chat.id] = question
    options = choose_options(question)

    # Preparing new buttons
    buttons = []
    for option in options:
        print(option)
        buttons.append(InlineKeyboardButton(text=option, callback_data=option))

    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    builder = InlineKeyboardBuilder.from_markup(markup)

    builder.adjust(1, 1, 1, 1)

    # Sending new message
    initial_message = await message.answer("Плотный салам\nКак переводится:\n\n"
                                           f"{question}",
                                           reply_markup=builder.as_markup())

    messages[message.chat.id].append(initial_message.message_id)


@dp.callback_query(lambda callback_query: callback_query.data in en_list)
async def check_translation(callback_query: types.callback_query):

    user_translation = callback_query.data
    correct_translation = word_dict[questions[callback_query.message.chat.id]]

    if user_translation == correct_translation:

        # Deleting previous messages
        for message_id in messages[callback_query.message.chat.id]:
            try:
                await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_id)
            except:
                continue
        messages[callback_query.message.chat.id] = []

        # Searching for a new question
        question, answer = choose_question()
        if answer is not None:
            greet_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                   text=f"Правильно, Валерий Игоревич оценил")
            messages[callback_query.message.chat.id].append(greet_message.message_id)
            while answer is not None:
                extra_info_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                            text=f"Глянь важную инфу\n\n{question}\n\n{answer}")
                messages[callback_query.message.chat.id].append(extra_info_message.message_id)
                question, answer = choose_question()

            new_question = f"Как переводится:\n\n{question}"
        else:
            new_question = f"Правильно, Валерий Игоревич оценил\n\nКак переводится:\n\n{question}"

        # Preparing new buttons
        questions[callback_query.message.chat.id] = question
        options = choose_options(question)

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
                                                      text=f"Неверно. Не разочаровывай, крутани еще раз")
        messages[callback_query.message.chat.id].append(wrong_answer_message.message_id)


if __name__ == '__main__':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG,
                        format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')
    asyncio.run(main())
