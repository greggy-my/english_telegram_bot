from db.database_manager import MongoDBManager


async def initiate_chat_data(user_id: int, chat_id: int):
    if not await MongoDBManager.check_user_id_existence(collection_name='chat_data', user_id=user_id):
        chat_data = {
            'user_id': user_id, 'chat_id': chat_id, 'messages': [], 'spin_correct_index': None,
            'spin_question': None,
            'spin_question_language': None,
            'write_translation_question': None,
            'write_translation_answer': None
        }
        await MongoDBManager.insert_chat_data(chat_data)
