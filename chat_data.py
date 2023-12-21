import json
import aiofiles
from collections import defaultdict
import os


def load_json_file(file_path, default_factory, key_transform=int):
    """Loads data from json file and returns default dictionary"""
    if file_path in os.listdir('data_storage'):
        with open(f'data_storage/{file_path}', 'r') as file:
            data = json.load(file,
                             object_hook=lambda x: {key_transform(k) if k.isdigit() else k: v for k, v in x.items()})
        return defaultdict(default_factory, data)
    else:
        return defaultdict(default_factory)


async def save_user_questions(questions: list) -> None:
    """Save users' last questions to a json file"""
    async with aiofiles.open('data_storage/questions.json', 'w') as file:
        await file.write(json.dumps(questions))


async def save_user_messages(messages: list) -> None:
    """Save users' chat messages to a json file"""
    async with aiofiles.open('data_storage/messages.json', 'w') as file:
        await file.write(json.dumps(messages))
