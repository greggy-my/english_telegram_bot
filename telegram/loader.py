import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode


class States:
    maintenance: bool = False


TOKEN = str(os.getenv('TOKEN_TEST'))
ADMIN = int(os.getenv('ADMIN'))
dp = Dispatcher(storage=RedisStorage.from_url('redis://localhost:6379/0'))
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)