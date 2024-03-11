from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_user_commands(bot: Bot):
    commands = [
        BotCommand(command='help', description='Помощь в работе с ботом'),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def set_description(bot: Bot):
    text = """
    🔎 Поиск: Найди нужное слово и его перевод.\n
    📚 Выбор Юнита: Выбери область обучения для Квиза и Правописания.\n
    🧠 Квиз: Проверь свои знания, выбирая правильный перевод слова на английском и русском. Твой прогресс сохраняется!\n
    ✍️ Правописание: Улучши свои навыки правописания слов на английском.\n
    📣 Обратная связь: Дай нам знать, как ты используешь бота!\n
    """
    await bot.set_my_description(description=text)