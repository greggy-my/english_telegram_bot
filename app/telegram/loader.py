from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.config import settings


class States:
    maintenance: bool = False


storage = RedisStorage.from_url(settings.REDIS_URL)
dp = Dispatcher(storage=storage)
bot = Bot(settings.TOKEN, parse_mode=ParseMode.HTML)