from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def admin_keyboard():
    """Creates admin keyboard builder"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='БД'),
    )
    return builder
