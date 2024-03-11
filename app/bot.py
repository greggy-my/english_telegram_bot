import asyncio
import logging
import sys
from aiogram import F
from aiogram.filters import CommandStart, Command, and_f, or_f

from telegram.handlers import admin, user_commands
from telegram.utils.bot_param_register import set_description, set_user_commands
from telegram.loader import dp, bot

from telegram.handlers.search import init_search, find_translation, cancel_search
from telegram.handlers.quiz import spin, check_translation, cancel_quiz
from db.user_progress import actualise_users_progress
from db.database_manager import create_tables
from translations.translation import Translation
from telegram.states.feedback import GetFeedback
from telegram.states.search import Search
from telegram.states.quiz import Quiz
from telegram.states.write_translation import WriteTranslation
from telegram.states.choose_unit import ChooseUnit
from telegram.handlers.write_translation import init_write_translation, send_question, check_answer, \
    show_right_translation, cancel_write_translation
from telegram.handlers.choose_unit import init_choose_unit, choose_unit, cancel_choose_unit, approve_choose_unit
from telegram.middleware.chat_action import ChatActionMiddleware


async def main() -> None:
    """Initiates the bot"""
    Translation.instantiate_from_excel()

    await set_user_commands(bot=bot)
    await set_description(bot=bot)
    await create_tables()

    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO,
                        format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')

    await actualise_users_progress()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


# middleware
dp.message.middleware.register(ChatActionMiddleware())

# admin
dp.startup.register(admin.start_bot)
dp.shutdown.register(admin.stop_bot)

# users commands
dp.message.register(user_commands.start, CommandStart())
dp.message.register(user_commands.send_instructions, Command(commands='help'))

# feedback
dp.message.register(user_commands.init_feedback, F.text == 'Обратная связь')
dp.message.register(user_commands.cancel_feedback, and_f(or_f(GetFeedback.feedback_text, GetFeedback.approve),
                                                         F.text == 'Отменить'))
dp.message.register(user_commands.approve_feedback, and_f(GetFeedback.approve,
                                                          F.text == 'Подтвердить'))
dp.message.register(user_commands.send_feedback, and_f(GetFeedback.feedback_text, F.text))

# quiz
dp.message.register(spin, F.text == 'Квиз')
dp.message.register(cancel_quiz, and_f(F.text == 'Назад в меню', Quiz.back_to_menu))
dp.callback_query.register(check_translation, Quiz.back_to_menu)

# search
dp.message.register(init_search, F.text == 'Поиск')
dp.message.register(cancel_search, and_f(F.text == 'Назад в меню', Search.back_to_menu))
dp.message.register(find_translation, and_f(F.text, Search.back_to_menu), flags={'chat_action': 'typing'})

# write translation
dp.message.register(init_write_translation,
                    F.text == 'Правописание')
dp.message.register(cancel_write_translation,
                    and_f(F.text == 'Назад в меню', WriteTranslation.back_to_menu))
dp.message.register(send_question,
                    and_f(F.text == 'Новый вопрос', WriteTranslation.back_to_menu))
dp.message.register(show_right_translation,
                    and_f(F.text == 'Проверить правильный ответ', WriteTranslation.back_to_menu))
dp.message.register(check_answer,
                    and_f(F.text, WriteTranslation.back_to_menu))

# choose unit
dp.message.register(init_choose_unit, F.text == 'Выбрать Юнит')
dp.message.register(cancel_choose_unit, and_f(or_f(ChooseUnit.unit, ChooseUnit.approve),
                                              F.text == 'Отменить'))
dp.message.register(approve_choose_unit, and_f(ChooseUnit.approve,
                                                          F.text == 'Подтвердить'))
dp.callback_query.register(choose_unit, or_f(ChooseUnit.unit, ChooseUnit.approve))

if __name__ == '__main__':
    asyncio.run(main())
