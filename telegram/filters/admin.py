from aiogram.filters import BaseFilter
from aiogram.types import Message
import os
from telegram.loader import ADMIN


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN
