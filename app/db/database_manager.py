import asyncio
from typing import Annotated

import motor.motor_asyncio
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings


class MongoDBManager:
    uri = settings.MONGO_URL
    db_name = 'english_bot'
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client[db_name]

    @classmethod
    async def find(cls, collection_name, query_data):
        collection = cls.db[collection_name]
        cursor = collection.find(*query_data)
        documents = await cursor.to_list(length=None)
        return documents

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


class ChatData(BaseModel):
    user_id: int
    chat_id: int
    messages: List[str] = Field(default_factory=list)
    chosen_unit: Optional[str] = None
    spin_correct_index: Optional[int] = None
    spin_question: Optional[str] = None
    spin_question_language: Optional[str] = None
    spin_question_unit: Optional[str] = None
    write_translation_question: Optional[str] = None
    write_translation_answer: Optional[str] = None
    write_translation_unit: Optional[str] = None

class UserProgress(BaseModel):
    user_id: int
    en_progress: Dict[str, int]
    ru_progress: Dict[str, int]


async_engine = create_async_engine(settings.POSTGRES_URL)
new_session = async_sessionmaker(async_engine, expire_on_commit=False)
intpk = Annotated[int, mapped_column(primary_key=True)]


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def drop_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


class Model(DeclarativeBase):
    pass


class FeedbackTable(Model):
    __tablename__ = "feedback"
    feedback_id: Mapped[intpk]
    feedback: Mapped[str]

class MagaTable(Model):
    __tablename__ = "maga"
    feedback_id: Mapped[intpk]
    feed: Mapped[str]

class FeedbackRepository:
    @classmethod
    async def add_data(cls, data: dict) -> int:
        async with new_session() as session:
            new_feedback = FeedbackTable(**data)
            session.add(new_feedback)
            await session.flush()
            await session.commit()
            return new_feedback.feedback_id

    @classmethod
    async def get_data(cls) -> list[dict]:
        async with new_session() as session:
            query = select(FeedbackTable)
            result = await session.execute(query)
            feedback_models = result.scalars().all()
            feedback_data = [feedback.__dict__ for feedback in feedback_models]
            for feedback in feedback_data:
                feedback.pop('_sa_instance_state', None)
            return feedback_data


if __name__ == '__main__':
    async def main():

        await MongoDBManager.delete_all_documents('user_progress')
        await MongoDBManager.delete_all_documents('chat_data')
        # # Example db_data
        # user_progress = {'user_id': 456, 'en_progress': {'bye': 0.01, 'hello': 0.05}, 'ru_progress': {'пока': 0.01, 'привет': 0.05}}
        # await MongoDBManager.insert_user_progress(user_progress)
        #
        chat_data = {'chat_id': 456, 'messages': [12, 323, 42], 'spin_correct_index': 1, 'spin_question': '',
                     'spin_question_language': '', 'write_translation_question': '', 'write_translation_answer': ''}
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