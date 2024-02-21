from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from translations.translation import Translation
from telegram.keyboards.quiz import quiz_inline_keyboard
from functions.quiz import choose_question, choose_options
from db.database_manager import MongoDBManager
from db.user_progress import update_user_progress


async def spin(message: Message) -> None:
    user_id = message.from_user.id
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)

    # Searching for a new question
    question, translation, question_language = choose_question(user_id=user_id)
    # Preparing new options
    options, right_option_index = choose_options(translation=translation, question_language=question_language)
    chat_data['spin_correct_answer'].append(right_option_index)

    # Creating a builder
    builder = quiz_inline_keyboard(options=options)

    # Sending new message
    game_message = await message.answer("Как переводится:\n\n"
                                        f"{question}",
                                        reply_markup=builder.as_markup())

    chat_data['messages'].append(game_message.message_id)
    chat_data['messages'].append(message.message_id)

    await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)


async def check_translation(callback_query: CallbackQuery, bot: Bot) -> None:
    """Check user's answer"""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    user_answer = int(callback_query.data)
    chat_data = await MongoDBManager.find_chat_data(user_id=user_id)
    right_option_index = chat_data['spin_correct_index']
    messages = chat_data['messages']
    question = chat_data['spin_question']
    question_language = chat_data['spin_question_language']

    if user_answer == right_option_index:
        # Deleting previous messages
        for message_id in messages:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                continue

        messages = []

        await update_user_progress(user_id=user_id,
                                   question_language=question_language,
                                   question=question,
                                   answer_status='right')

        greet_message = await callback_query.message.reply(text=f"Правильно, Валерий Игоревич оценил")
        messages.append(greet_message.message_id)

        # Searching for a new question
        question, translation, question_language = choose_question(user_id=user_id)

        # Preparing new options
        options, right_option_index = choose_options(translation=translation, question_language=question_language)
        chat_data['spin_correct_answer'] = right_option_index

        # Creating a builder
        builder = quiz_inline_keyboard(options=options)

        # Sending new markup
        new_question_message = await callback_query.message.answer(text=f"Как переводится:\n\n{question}",
                                                                   reply_markup=builder.as_markup())
        messages.append(new_question_message.message_id)

        await MongoDBManager.update_chat_data(user_id=user_id, new_data=chat_data)

    else:
        # Wrong answer message
        wrong_answer_message = await bot.send_message(chat_id=callback_query.message.chat.id,
                                                      text=f"Неверно. Не разочаровывай, выбери еще раз")
        await update_user_progress(user_id=user_id,
                                   question_language=question_language,
                                   question=question,
                                   answer_status='wrong')

        messages.append(wrong_answer_message.message_id)


