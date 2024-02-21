from database_manager import MongoDBManager


async def initiate_chat_data(chat_id: int):
    chat_data = {'chat_id': chat_id, 'messages': [], 'spin_correct_answer': None}
    await MongoDBManager.insert_chat_data(chat_data)
