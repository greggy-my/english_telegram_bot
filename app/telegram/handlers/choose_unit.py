from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.db.database_manager import MongoDBManager
from app.telegram.keyboards.choose_unit import (
    approve_choose_unit_keyboard,
    cancel_choose_unit_keyboard,
    inline_choose_unit,
)
from app.telegram.keyboards.menu import main_menu
from app.telegram.states.choose_unit import ChooseUnit


async def init_choose_unit(message: Message, state: FSMContext) -> None:
    """Initialises the feedback"""
    user_id = message.from_user.id
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)

    initial_text = '<i>Выбери Юнит, по которому будешь проходить задания:</i>'
    init_unit_message = \
        await message.answer(text=initial_text,
                             reply_markup=cancel_choose_unit_keyboard().as_markup(resize_keyboard=True))

    inline_choice_text = 'Юниты:'
    inline_choice_message = \
        await message.answer(text=inline_choice_text, reply_markup=inline_choose_unit().as_markup(resize_keyboard=True))

    chat_data['messages'].append(init_unit_message.message_id)
    chat_data['messages'].append(inline_choice_message.message_id)

    await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)

    await state.set_state(ChooseUnit.unit)


async def choose_unit(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(unit=callback_query.data)
    await callback_query.message.answer(
        text=f'Подтверди выбор Юнита:\n\n{callback_query.data.capitalize()}',
        reply_markup=approve_choose_unit_keyboard().as_markup(resize_keyboard=True)
    )

    await state.set_state(ChooseUnit.approve)


async def approve_choose_unit(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    user_id = message.from_user.id
    chosen_unit = user_data['unit']

    if chosen_unit.lower() == 'все':
        chosen_unit = None

    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)

    for message_id in chat_data['messages']:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except Exception:
            continue

    await message.answer(text='<i>Обратно в меню</i>', reply_markup=main_menu().as_markup(resize_keyboard=True))
    await MongoDBManager.update_chat_data(user_id=user_id,
                                          new_data={'chosen_unit': chosen_unit, 'messages': []})
    await state.clear()


async def cancel_choose_unit(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)

    for message_id in chat_data['messages']:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except Exception:
            continue

    await MongoDBManager.update_chat_data(user_id=user_id, new_data={'messages': []})

    await message.answer(text='<i>Обратно в меню</i>', reply_markup=main_menu().as_markup(resize_keyboard=True))
    await state.clear()
