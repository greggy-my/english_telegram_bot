from aiogram.filters import BaseFilter
from bot import ADMIN
from aiogram.types import Message


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN
