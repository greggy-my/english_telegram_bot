import random
from translations.translation import Translation
from db.database_manager import MongoDBManager


async def choose_question(user_id: int, chosen_unit: str) -> tuple[str, str, str, str]:
    """Returns a randomly chosen question"""

    language_choice = random.randint(0, 1)

    options_mapping = {
            0: {'user_progress': 'ru_progress', 'language': 'russian', 'dict': Translation.ru_word_dict},
            1: {'user_progress': 'en_progress', 'language': 'english', 'dict': Translation.en_word_dict}
    }

    choice_map = options_mapping[language_choice]

    user_progress = await MongoDBManager.find_user_progress(user_id=user_id)

    if chosen_unit is not None:
        questions = list(filter(lambda x: f'{chosen_unit}_' in x, user_progress[choice_map['user_progress']].keys()))
        weights = [user_progress[choice_map['user_progress']][question] for question in questions]
    else:
        questions = list(user_progress[choice_map['user_progress']].keys())
        weights = list(user_progress[choice_map['user_progress']].values())

    choice = random.choices(questions, weights=weights, k=1)[0]
    question_unit = choice.split('_', 1)[0]
    question = choice.split('_', 1)[1]
    translation = choice_map['dict'][question]
    language = choice_map['language']

    return question_unit, question, translation, language


def choose_options(translation: str, question_language: str) -> tuple[list[str], int]:
    """Return a randomly chosen answer options"""

    word_list = Translation.en_list if question_language == 'russian' else Translation.ru_list

    options = [random.choice(word_list).split('_', 1)[1] for _ in range(3)]
    options.append(translation)
    random.shuffle(options)
    right_option_index = options.index(translation)
    return options, right_option_index
