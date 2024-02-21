from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot import States


class InMaintenance(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return States.maintenance


class NotInMaintenance(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return not States.maintenance
