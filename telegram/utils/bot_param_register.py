from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_user_commands(bot: Bot):
    commands = [
        BotCommand(command='help', description='Помощь в работе с ботом'),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def set_description(bot: Bot):
    text = """
    🏁 Запуск\nНачните общаться с чат-ботом, отправив сообщение с вопросом, который вас интересует.\n\n💬 Общение\nЕсли бот не может вам ответить или его ответ не содержит нужной вам информации, попробуйте сформулировать вопрос точнее.\n\n❔Помощь\nЕсли вы не получили ответ на ваш вопрос, напишите вашему HR-менеджеру или на welcome@loodsen.ru.
    """
    await bot.set_my_description(description=text)