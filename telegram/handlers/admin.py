import aiogram.exceptions
from aiogram.types import Message
from aiogram import Bot
from bot import ADMIN, States
from telegram.keyboards.admin import admin_keyboard


async def start_bot(bot: Bot) -> None:
    """Sends the start bot message to admins"""
    try:
        await bot.send_message(ADMIN, text='Бот запущен', reply_markup=admin_keyboard().as_markup(resize_keyboard=True))
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
