from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from telegram.keyboards.quiz import quiz_inline_keyboard
from functions.quiz import choose_question, choose_options

from db.database_manager import MongoDBManager
from db.user_progress import update_user_progress

from telegram.states.quiz import Quiz
from telegram.keyboards.menu import main_menu, back_to_menu


async def spin(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)
    chosen_unit = chat_data['chosen_unit']
    initial_text = 'Ты в режиме Квиза'
    await message.answer(
        text=initial_text,
        reply_markup=back_to_menu().as_markup(resize_keyboard=True)
    )

    # Searching for a new question
    question_unit, question, translation, question_language =\
        await choose_question(user_id=user_id, chosen_unit=chosen_unit)

    # Preparing new options
    options, right_option_index = choose_options(translation=translation, question_language=question_language)
    chat_data['spin_question_unit'] = question_unit
    chat_data['spin_correct_index'] = right_option_index
    chat_data['spin_question'] = question
    chat_data['spin_question_language'] = question_language

    # Creating a builder
    builder = quiz_inline_keyboard(options=options)

    # Sending new message
    game_message = await message.answer('Как переводится:\n'
                                        f'"{question.capitalize()}"',
                                        reply_markup=builder.as_markup(resize_keyboard=True))

    chat_data['messages'].append(game_message.message_id)
    chat_data['messages'].append(message.message_id)

    await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)
    await state.set_state(Quiz.back_to_menu)


async def check_translation(callback_query: CallbackQuery, bot: Bot) -> None:
    """Check user's answer"""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    user_answer = int(callback_query.data)
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)
    right_option_index = chat_data['spin_correct_index']
    messages = chat_data['messages']
    chosen_unit = chat_data['chosen_unit']
    question = chat_data['spin_question']
    question_language = chat_data['spin_question_language']
    question_unit = chat_data['spin_question_unit']

    if user_answer == right_option_index:
        # Deleting previous messages
        for message_id in messages:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                continue

        chat_data['messages'] = []

        await update_user_progress(user_id=user_id,
                                   question_language=question_language,
                                   question=question,
                                   question_unit=question_unit,
                                   answer_status='right')

        # Searching for a new question
        question_unit, question, translation, question_language =\
            await choose_question(user_id=user_id, chosen_unit=chosen_unit)

        # Preparing new options
        options, right_option_index = choose_options(translation=translation, question_language=question_language)
        chat_data['spin_question_unit'] = question_unit
        chat_data['spin_correct_index'] = right_option_index
        chat_data['spin_question'] = question
        chat_data['spin_question_language'] = question_language

        # Creating a builder
        builder = quiz_inline_keyboard(options=options)

        # Sending new markup
        new_question_message = await bot.send_message(chat_id=chat_id,
                                                      text=f'Как переводится:\n"{question.capitalize()}"',
                                                      reply_markup=builder.as_markup(resize_keyboard=True))
        chat_data['messages'] .append(new_question_message.message_id)

        await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)

    else:
        # Wrong answer message
        wrong_answer_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=f'Неверно. Не разочаровывай, выбери еще раз')
        await update_user_progress(user_id=user_id,
                                   question_language=question_language,
                                   question=question,
                                   question_unit=question_unit,
                                   answer_status='wrong')

        chat_data['messages'] .append(wrong_answer_message.message_id)

        await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)


async def cancel_quiz(message: Message, state: FSMContext, bot: Bot):
    chat_data = await MongoDBManager.find_chat_data(user_id=message.from_user.id)

    for message_id in chat_data['messages']:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
        except Exception:
            continue

    await message.answer(
        text='Обратно в главное меню',
        reply_markup=main_menu().as_markup(resize_keyboard=True)
    )
    await state.clear()
