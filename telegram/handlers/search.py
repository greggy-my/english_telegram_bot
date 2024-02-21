from aiogram.types import Message
from translations.search_alg import HashSearch, EmbeddingSearch
from db.database_manager import MongoDBManager


async def find_translation(message: Message) -> None:
    """React to a user message"""

    found_word, found_translation = EmbeddingSearch.search(query=message.text)
    found_word_hash, found_translation_hash = HashSearch.search(query=message.text)

    if found_word is None:
        await message.reply(text=f"Ошибочка вышла:\n\nНе смог найти")

    elif (found_word == found_word_hash) or (found_word_hash is None):
        await message.reply(text=f"Ты это искал:\n\nФраза: {found_word}\n\nПеревод: {found_translation}")

    else:
        await message.reply(text=f"Для тебя есть два варианта:"
                                 f"\n\nФраза: {found_word}\n\nПеревод: {found_translation}\n\n"
                                 f"Фраза: {found_word_hash}\n\nПеревод: {found_translation_hash}")
