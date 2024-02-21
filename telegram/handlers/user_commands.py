from aiogram import Bot
from aiogram.types import Message
from db.user_progress import initiate_user_progress


async def send_instructions(message: Message) -> None:
    """React to the Instruct command"""
    text = """
            1. Для вызова игры в меню используйте функцию 'Крути барабан', которая запустит игру с выбором правильного перевода слова. Вам могут выпадать сообщения с идиомами после прокрутки барабана
            
            2. Чат сохраняет ваш прогресс. Отвечаете правильно - этот вопрос будет попадаться все меньше, и наоборот
            
            3. Если вы напишете сообщение в чат вам вернется найденное слово и его перевод на основе вашего сообщения. Рекомендую потестировать, написав пару неполных слов
            """
    await message.reply(text=text)


async def start(message: Message) -> None:
    """React to the Start command"""
    user_id = message.from_user.id
    await initiate_user_progress(user_id=user_id)
    await message.answer(text="Плотный салам")