from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def write_translation_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Проверить правильный ответ'),
        types.KeyboardButton(text='Новый вопрос'),
        types.KeyboardButton(text='Назад в меню'),
    )

    builder.adjust(2, 1)

    return builder
