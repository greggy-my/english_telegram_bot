from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from db.database_manager import MongoDBManager
from functions.write_translation import choose_ru_question

from telegram.states.write_translation import WriteTranslation
from telegram.keyboards.write_translation import write_translation_menu
from telegram.keyboards.menu import main_menu


async def send_question(message: Message):
    user_id = message.from_user.id
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)
    chosen_unit = chat_data['chosen_unit']
    question, translation = choose_ru_question(chosen_unit=chosen_unit)

    chat_data['write_translation_question'] = question
    chat_data['write_translation_answer'] = translation

    await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)

    question_text = f'Напиши перевод слова "{question.capitalize()}" на Английском'
    await message.answer(text=question_text,
                         reply_markup=write_translation_menu().as_markup(resize_keyboard=True))


async def init_write_translation(message: Message, state: FSMContext) -> None:
    initial_text = '<i>В режиме Правописание</i>'
    await message.answer(text=initial_text, reply_markup=write_translation_menu().as_markup(resize_keyboard=True))

    await state.set_state(WriteTranslation.back_to_menu)
    await send_question(message=message)


async def check_answer(message: Message):
    user_id = message.from_user.id
    user_answer = message.text

    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)

    right_answer = chat_data['write_translation_answer']

    if user_answer.lower().strip() == right_answer.lower():

        right_text = f'Молодец, все верно!'
        await message.answer(text=right_text)

        await send_question(message=message)

    else:

        wrong_text = f'Не совсем так, попробуй еще раз'
        await message.answer(text=wrong_text)


async def show_right_translation(message: Message):
    user_id = message.from_user.id
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)
    right_answer = chat_data['write_translation_answer']

    right_answer_text = f'Правильный ответ: {right_answer.capitalize()}'
    await message.answer(text=right_answer_text)


async def cancel_write_translation(message: Message, state: FSMContext):
    await message.answer(text='<i>Обратно в меню</i>', reply_markup=main_menu().as_markup(resize_keyboard=True))

    await state.clear()
