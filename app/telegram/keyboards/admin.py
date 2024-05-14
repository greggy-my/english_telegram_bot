from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_keyboard():
    """Creates admin keyboard builder"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='БД'),
    )
    return builder
