import aiogram.exceptions
from aiogram.types import Message
from aiogram import Bot
from telegram.loader import ADMIN, States


async def start_bot(bot: Bot) -> None:
    """Sends the start bot message to admins"""
    try:
        await bot.send_message(ADMIN, text='Бот запущен')
    except aiogram.exceptions.TelegramBadRequest as se:
        print(f'Error while sending start message to admin ({ADMIN}): {se}')


async def stop_bot(bot: Bot) -> None:
    """Sends the stop_servers bot message to admins"""
    try:
        await bot.send_message(ADMIN, text='Бот выключен')
    except aiogram.exceptions.TelegramBadRequest as ce:
        print(f'Error while sending close message to admin ({ADMIN}): {ce}')


async def maintenance(message: Message, bot: Bot) -> None:
    """Puts bot into maintenance mode"""
    if States.maintenance:
        States.maintenance = False
        try:
            await bot.send_message(ADMIN, text='Бот в обычном режиме')
        except aiogram.exceptions.TelegramBadRequest as me:
            print(f'Error while sending maintenance message to admin ({ADMIN}): {me}')
    else:
        States.maintenance = True
        try:
            await bot.send_message(ADMIN, text='Бот в режиме тех. обслуживания')
        except aiogram.exceptions.TelegramBadRequest as me:
            print(f'Error while sending maintenance message to admin ({ADMIN}): {me}')
