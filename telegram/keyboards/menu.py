from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Поиск'),
        types.KeyboardButton(text='Квиз'),
        types.KeyboardButton(text='Правописание'),
        types.KeyboardButton(text='Обратная связь'),
        types.KeyboardButton(text='Выбрать Юнит'),
    )
    builder.adjust(2, 2, 1)

    return builder


def back_to_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Назад в меню'),
    )
    return builder
