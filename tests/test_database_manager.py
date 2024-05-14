import asyncio

import pytest
from copy import deepcopy
from contextlib import nullcontext as does_not_raise

from app.db.database_manager import MongoDBManager


@pytest.mark.asyncio
async def test_chat_data(chats, setup_mongodb):
    for chat in chats:
        await MongoDBManager.insert_chat_data(deepcopy(chat.__dict__))
        chat_data = await MongoDBManager.find_chat_data(chat.user_id)
        chat_data.pop('_id', None)
        assert chat.__dict__ == chat_data