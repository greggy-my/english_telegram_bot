import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode


class States:
    maintenance: bool = False


TOKEN = str(os.getenv('TOKEN_TEST'))
ADMIN = int(os.getenv('ADMIN'))
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)