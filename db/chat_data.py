from db.database_manager import MongoDBManager


async def initiate_chat_data(user_id: int, chat_id: int):
    chat_data = {'user_id': user_id, 'chat_id': chat_id, 'messages': [], 'spin_correct_index': None,
                 'spin_question': None,
                 'spin_question_language': None}
    await MongoDBManager.insert_chat_data(chat_data)
