import aiogram.exceptions
from aiogram import Bot

from app.config import settings


async def start_bot(bot: Bot) -> None:
    """Sends the start bot message to admins"""
    try:
        await bot.send_message(settings.ADMIN, text='Бот запущен')
    except aiogram.exceptions.TelegramBadRequest as se:
        print(f'Error while sending start message to admin ({settings.ADMIN}): {se}')


async def stop_bot(bot: Bot) -> None:
    """Sends the stop_servers bot message to admins"""
    try:
        await bot.send_message(settings.ADMIN, text='Бот выключен')
    except aiogram.exceptions.TelegramBadRequest as ce:
        print(f'Error while sending close message to admin ({settings.ADMIN}): {ce}')
