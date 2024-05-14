from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.telegram.keyboards.menu import back_to_menu, main_menu
from app.telegram.states.search import Search
from app.translations.search_alg import HashSearch


async def init_search(message: Message, state: FSMContext) -> None:
    """Initialises the feedback"""
    await message.answer(text='<i>В режиме Поиск</i>', reply_markup=back_to_menu().as_markup(resize_keyboard=True))

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
    await message.answer(text='<i>Обратно в меню</i>', reply_markup=main_menu().as_markup(resize_keyboard=True))

    await state.clear()
