from collections import defaultdict
import json
import aiofiles


def actualise_user_progress(users_progress_weights_en: defaultdict,
                            users_progress_weights_ru: defaultdict,
                            en_list: list, ru_list: list) -> None:
    """Update users' progress comparing it with current word population"""
    all_questions_en = set(en_list)
    all_questions_ru = set(ru_list)

    def update(users_progress_weights, all_questions):
        for user, user_progress in users_progress_weights.items():
            questions_user = set(user_progress.keys())
            questions_add = all_questions - questions_user
            questions_delete = questions_user - all_questions

            for question in questions_delete:
                user_progress.pop(question, None)

            for question in questions_add:
                user_progress[question] = 1

    update(users_progress_weights_en, all_questions_en)
    update(users_progress_weights_ru, all_questions_ru)


async def initiate_user_progress(user_id: int,
                                 users_progress_weights_en: defaultdict,
                                 users_progress_weights_ru: defaultdict,
                                 en_list: list, ru_list: list) -> None:
    """Create user progress weights array for a new user or extends the array if new words were added to the db"""
    if user_id not in users_progress_weights_en.keys():
        users_progress_weights_en[user_id] = {word: 1 for word in en_list}
    if user_id not in users_progress_weights_ru.keys():
        users_progress_weights_ru[user_id] = {word: 1 for word in ru_list}


async def update_user_progress(user_id: str,
                               question: str,
                               question_language: str,
                               answer_status: str,
                               users_progress_weights_en: defaultdict,
                               users_progress_weights_ru: defaultdict
                               ) -> None:
    """Update progress weights after answering a question"""
    if user_id in users_progress_weights_en.keys():
        if question_language == 'russian':
            progress = users_progress_weights_ru
        else:
            progress = users_progress_weights_en

        if answer_status == 'right':
            coefficient = 0.5
        else:
            coefficient = 1.5

        progress[user_id][question] = round(
            progress[user_id][question] * coefficient, 4)


async def save_user_progress(question_language: str,
                             users_progress_weights_en: defaultdict,
                             users_progress_weights_ru: defaultdict
                             ) -> None:
    """Save users' progress to a json file"""
    if question_language == 'russian':
        async with aiofiles.open('data_storage/users_progress_ru.json', 'w') as file:
            await file.write(json.dumps(users_progress_weights_ru))
    else:
        async with aiofiles.open('data_storage/users_progress_en.json', 'w') as file:
            await file.write(json.dumps(users_progress_weights_en))
