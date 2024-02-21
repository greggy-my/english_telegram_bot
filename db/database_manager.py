import motor.motor_asyncio
import asyncio


class MongoDBManager:
    uri = 'mongodb://localhost:27017'
    db_name = 'bot'
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client[db_name]

    @classmethod
    async def find_all_documents(cls, collection_name):
        collection = cls.db[collection_name]
        cursor = collection.find({})
        documents = await cursor.to_list(length=None)
        return documents

    @classmethod
    async def insert_chat_data(cls, data):
        chat_data_collection = cls.db.chat_data
        await chat_data_collection.insert_one(data)

    @classmethod
    async def insert_user_progress(cls, data):
        user_progress_collection = cls.db.user_progress
        await user_progress_collection.insert_one(data)

    @classmethod
    async def find_chat_data(cls, user_id):
        chat_data_collection = cls.db.chat_data
        document = await chat_data_collection.find_one({'user_id': user_id})
        return document

    @classmethod
    async def find_user_progress(cls, user_id):
        user_progress_collection = cls.db.user_progress
        document = await user_progress_collection.find_one({'user_id': user_id})
        return document

    @classmethod
    async def update_chat_data(cls, user_id, new_data):
        chat_data_collection = cls.db.chat_data
        await chat_data_collection.update_one({'user_id': user_id}, {'$set': new_data})

    @classmethod
    async def update_user_progress(cls, user_id, new_data):
        user_progress_collection = cls.db.user_progress
        await user_progress_collection.update_one({'user_id': user_id}, {'$set': new_data})

    @classmethod
    async def check_user_id_existence(cls, collection_name, user_id):
        collection = cls.db[collection_name]
        document_count = await collection.count_documents({'user_id': user_id})
        return document_count > 0

    @classmethod
    async def delete_one_document(cls, collection_name, filter_query):
        collection = cls.db[collection_name]
        result = await collection.delete_one(filter_query)
        return result.deleted_count

    @classmethod
    async def delete_all_documents(cls, collection_name):
        collection = cls.db[collection_name]
        result = await collection.delete_many({})
        return result.deleted_count


if __name__ == '__main__':
    async def main():

        await MongoDBManager.delete_all_documents('user_progress')
        await MongoDBManager.delete_all_documents('chat_data')
        # # Example data
        # user_progress = {'user_id': 456, 'en_progress': {'bye': 0.01, 'hello': 0.05}, 'ru_progress': {'пока': 0.01, 'привет': 0.05}}
        # await MongoDBManager.insert_user_progress(user_progress)
        #
        chat_data = {'chat_id': 456, 'messages': [12, 323, 42], 'spin_correct_index': 1, 'spin_question': '',
                     'spin_question_language': ''}
        # await MongoDBManager.insert_chat_data(chat_data)
        #
        # # Find all documents
        # all_chat_data = await MongoDBManager.find_all_documents('chat_data')
        # all_user_progress = await MongoDBManager.find_all_documents('user_progress')
        #
        # print("All Chat Data:")
        # for document in all_chat_data:
        #     print(document)
        #
        # print("\nAll User Progress:")
        # for document in all_user_progress:
        #     print(document)


    # Run the event loop
    asyncio.run(main())