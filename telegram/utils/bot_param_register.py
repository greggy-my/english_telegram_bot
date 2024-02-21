from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_user_commands(bot: Bot):
    commands = [
        BotCommand(command='help', description='Помощь в работе с ботом'),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def set_description(bot: Bot):
    text = """
    Даров
    """
    await bot.set_my_description(description=text)