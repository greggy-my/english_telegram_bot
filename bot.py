import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, and_f
from telegram.handlers import admin, user_commands
from telegram.filters.admin import IsAdmin
from telegram.utils.bot_param_register import set_description, set_user_commands
from db.user_progress import actualise_users_progress


class States:
    maintenance: bool = False


TOKEN = str(os.getenv('TOKEN_TEST'))
ADMIN = int(os.getenv('ADMIN'))
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def main() -> None:
    """Initiates the bot"""
    await set_user_commands(bot)
    await set_description(bot)
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO,
                        format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')
    await actualise_users_progress()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


# admin
dp.startup.register(admin.start_bot)
dp.shutdown.register(admin.stop_bot)
dp.message.register(admin.maintenance, and_f(IsAdmin(), F.text == 'Тех обслуживание'))

# users
dp.message.register(user_commands.start, CommandStart())
dp.message.register(user_commands.send_instructions, Command(commands='help'))


if __name__ == '__main__':
    asyncio.run(main())
