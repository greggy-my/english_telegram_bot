import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from config import redis_url


class States:
    maintenance: bool = False


TOKEN = str(os.getenv('TOKEN'))
ADMIN = int(os.getenv('ADMIN'))
dp = Dispatcher(storage=RedisStorage.from_url(redis_url))
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)