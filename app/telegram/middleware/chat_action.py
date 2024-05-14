from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from app.telegram.loader import bot


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]
                       ) -> Any:
        chat_action = get_flag(data, 'chat_action')
        if not chat_action:
            return await handler(event, data)

        async with ChatActionSender(chat_id=event.chat.id, bot=bot, action=chat_action):
            return await handler(event, data)