import asyncio

import pytest
import pytest_asyncio

from app.config import settings
from app.db.database_manager import Model, MongoDBManager, UserProgress, ChatData, drop_tables, create_tables

# @pytest.fixture(scope="session")
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()

# @pytest.fixture(scope="session", autouse=True)
# async def setup_sqlalchemy_db(loop):
#     assert settings.MODE == "TEST"
#     await create_tables()
#     yield
#     await drop_tables()


@pytest_asyncio.fixture()
async def setup_mongodb():
    assert settings.MODE == "TEST"
    yield
    await MongoDBManager.delete_all_documents('chat_data')
    await MongoDBManager.delete_all_documents('user_progress')

@pytest.fixture
def chats():
    chats = [
        ChatData(user_id=1, chat_id=1),
        ChatData(user_id=2, chat_id=2)
    ]
    return chats

@pytest.fixture
def user_progress():
    user_progress = [
        UserProgress(user_id=1, en_progress={'hi': 1}, ru_progress={'привет': 1}),
        UserProgress(user_id=2, en_progress={'hi': 1}, ru_progress={'привет': 1})
    ]
    return user_progress