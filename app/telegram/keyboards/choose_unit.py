from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.translations.translation import Translation


def inline_choose_unit():
    # Preparing new buttons
    buttons = []
    for unit in Translation.units:
        buttons.append(InlineKeyboardButton(text=unit.capitalize(), callback_data=unit))

    buttons.append(InlineKeyboardButton(text='Все юниты', callback_data='все'))
    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    builder = InlineKeyboardBuilder.from_markup(markup)

    builder.adjust(*(1 for _ in range(1, len(Translation.units)+1)))

    return builder


def cancel_choose_unit_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Отменить')
    )
    return builder


def approve_choose_unit_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Отменить'),
        types.KeyboardButton(text='Подтвердить')
    )
    return builder
