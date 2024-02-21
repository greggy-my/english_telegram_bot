from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Поиск'),
        types.KeyboardButton(text='Квиз'),
        types.KeyboardButton(text='Правописание'),
        types.KeyboardButton(text='Обратная связь'),
    )
    return builder


def back_to_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Назад в меню'),
    )
    return builder
