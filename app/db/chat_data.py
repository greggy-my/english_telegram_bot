from .database_manager import MongoDBManager, ChatData


async def initiate_chat_data(user_id: int, chat_id: int):
    if not await MongoDBManager.check_user_id_existence(collection_name='chat_data', user_id=user_id):
        chat_data = ChatData(user_id=user_id, chat_id=chat_id)
        await MongoDBManager.insert_chat_data(chat_data.__dict__)
