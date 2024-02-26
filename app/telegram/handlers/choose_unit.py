from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from db.database_manager import MongoDBManager

from telegram.states.choose_unit import ChooseUnit
from telegram.keyboards.menu import main_menu
from telegram.keyboards.choose_unit import inline_choose_unit, approve_choose_unit_keyboard, cancel_choose_unit_keyboard


async def init_choose_unit(message: Message, state: FSMContext) -> None:
    """Initialises the feedback"""
    initial_text = 'Выбери Юнит, по которому будешь проходить задания:'
    await message.answer(text=initial_text, reply_markup=cancel_choose_unit_keyboard().as_markup(resize_keyboard=True))

    inline_choice_text = 'Юниты:'
    await message.answer(text=inline_choice_text, reply_markup=inline_choose_unit().as_markup(resize_keyboard=True))
    await state.set_state(ChooseUnit.unit)


async def choose_unit(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(unit=callback_query.data)
    await callback_query.message.answer(
        text=f'Подтвердите выбор Юнита:\n\n{callback_query.data.capitalize()}',
        reply_markup=approve_choose_unit_keyboard().as_markup(resize_keyboard=True)
    )
    await state.set_state(ChooseUnit.approve)


async def approve_choose_unit(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_unit = user_data['unit']

    if chosen_unit.lower() == 'все':
        chosen_unit = None

    await MongoDBManager.update_chat_data(user_id=message.from_user.id,
                                          new_data={'chosen_unit': chosen_unit})

    await message.answer(
        text=f'Выбор Юнита подтвержден',
        reply_markup=main_menu().as_markup(resize_keyboard=True)
    )

    await state.clear()


async def cancel_choose_unit(message: Message, state: FSMContext):
    await message.answer(
        text='Назад в главное меню',
        reply_markup=main_menu().as_markup(resize_keyboard=True)
    )

    await state.clear()
