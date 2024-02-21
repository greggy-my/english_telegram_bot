from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cancel_feedback_keyboard():
    """Creates feedback keyboard builder"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Отменить')
    )
    return builder


def approve_feedback_keyboard():
    """Creates feedback keyboard builder"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Отменить'),
        types.KeyboardButton(text='Подтвердить')
    )
    return builder
