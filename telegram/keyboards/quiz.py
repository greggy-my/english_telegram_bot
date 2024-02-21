from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from functions.quiz import choose_options


def quiz_inline_keyboard(options: list[str]) -> InlineKeyboardBuilder:
    """Return an InlineKeyboardBuilder based on a chosen question and options"""
    # Preparing new buttons
    buttons = []
    for index, option in enumerate(options):
        buttons.append(InlineKeyboardButton(text=option, callback_data=str(index)))

    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    builder = InlineKeyboardBuilder.from_markup(markup)

    builder.adjust(1, 1, 1, 1)

    return builder
