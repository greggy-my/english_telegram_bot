from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from translations.search_alg import HashSearch
from telegram.states.search import Search
from telegram.keyboards.menu import main_menu, back_to_menu


async def init_search(message: Message, state: FSMContext) -> None:
    """Initialises the feedback"""
    initial_text = 'Ты в режиме поиска перевода слов'
    await message.answer(
        text=initial_text,
        reply_markup=back_to_menu().as_markup(resize_keyboard=True)
    )
    await state.set_state(Search.back_to_menu)


async def find_translation(message: Message) -> None:
    """React to a user message"""

    found_word_hash, found_translation_hash = HashSearch.search(query=message.text)

    if found_word_hash is None:
        await message.reply(text=f"Ошибочка вышла:\n\nНе смог найти")

    else:
        await message.reply(text=f"Ты это искал:\n\nФраза: {found_word_hash.capitalize()}"
                                 f"\n\nПеревод: {found_translation_hash.capitalize()}")


async def cancel_search(message: Message, state: FSMContext):
    await message.answer(
        text='Обратно в главное меню',
        reply_markup=main_menu().as_markup(resize_keyboard=True)
    )
    await state.clear()
