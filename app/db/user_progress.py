import asyncio

from app.translations.translation import Translation

from .database_manager import MongoDBManager, UserProgress


async def actualise_users_progress() -> None:
    """Update users' progress comparing it with current word population"""

    if len(Translation.en_list) == 0 or len(Translation.ru_list) == 0:
        raise Exception('Translation is empty')

    users_documents = await MongoDBManager.find_all_documents('user_progress')
    all_questions_en = set(Translation.en_list)
    all_questions_ru = set(Translation.ru_list)

    for doc in users_documents:
        # russian
        current_progress_ru = doc.get('ru_progress')
        user_questions_ru = set(current_progress_ru.keys())
        new_questions_ru = all_questions_ru - user_questions_ru
        questions_to_delete_ru = user_questions_ru - all_questions_ru

        for question in questions_to_delete_ru:
            current_progress_ru.pop(question, None)

        for question in new_questions_ru:
            current_progress_ru[question] = 1

        # english
        current_progress_en = doc.get('en_progress')
        user_questions_en = set(current_progress_en.keys())
        new_questions_en = all_questions_en - user_questions_en
        questions_to_delete_en = user_questions_en - all_questions_en

        for question in questions_to_delete_en:
            current_progress_en.pop(question, None)

        for question in new_questions_en:
            current_progress_en[question] = 1

        await MongoDBManager.update_user_progress(user_id=doc.get('user_id'),
                                                  new_data={'en_progress': current_progress_en,
                                                            'ru_progress': current_progress_ru})


async def initiate_user_progress(user_id: int) -> None:
    """Create user progress weights array for a new user or extends the array if new words were added to the db"""
    if not await MongoDBManager.check_user_id_existence(collection_name='user_progress', user_id=user_id):
        ru_progress = {word_key: 1 for word_key in Translation.ru_list}
        en_progress = {word_key: 1 for word_key in Translation.en_list}
        user_progress = UserProgress(user_id=user_id, en_progress=en_progress, ru_progress=ru_progress)
        await MongoDBManager.insert_user_progress(user_progress.__dict__)


async def update_user_progress(user_id: int,
                               question: str,
                               question_language: str,
                               question_unit: str,
                               answer_status: str) -> None:
    """Update progress weights after answering a question"""

    if question_language == 'russian':
        progress = 'ru_progress'
    else:
        progress = 'en_progress'

    if answer_status == 'right':
        coefficient = 0.5
    else:
        coefficient = 1.5

    user_progress = await MongoDBManager.find_user_progress(user_id=user_id)

    user_progress[progress][f'{question_unit}_{question}'] =\
        round(user_progress[progress][f'{question_unit}_{question}'] * coefficient, 4)

    await MongoDBManager.update_user_progress(user_id=user_id, new_data=user_progress)


if __name__ == '__main__':
    async def main():
        Translation.instantiate_from_excel()
        await initiate_user_progress(user_id=665)
        # await actualise_user_progress()
        await update_user_progress(user_id=665, question='организационная структура', question_language='russian', answer_status='right')
        all_chat_data = await MongoDBManager.find_all_documents('chat_data')
        all_user_progress = await MongoDBManager.find_all_documents('user_progress')

        print("\nAll Chat Data:")
        for document in all_chat_data:
            print(document)

        print("\nAll User Progress:")
        for document in all_user_progress:
            print(document)

    asyncio.run(main())