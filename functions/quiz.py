import random
from collections import defaultdict
from translations.translation import Translation
from db.database_manager import MongoDBManager


def choose_question(user_id: int) -> tuple[str, str, str]:
    """Returns a randomly chosen question"""

    language_choice = random.randint(0, 1)

    options_mapping = {
            0: {'user_progress': 'ru_progress', 'language': 'russian', 'dict': Translation.ru_word_dict},
            1: {'user_progress': 'en_progress', 'language': 'english', 'dict': Translation.en_word_dict}
    }

    choice_map = options_mapping[language_choice]
    user_progress = await MongoDBManager.find_user_progress(user_id=user_id)
    questions = user_progress[choice_map['user_progress']].keys()
    weights = user_progress[choice_map['user_progress']].values()
    question = random.choices(questions, weights=weights, k=1)[0]
    translation = choice_map['dict'][question]
    language = choice_map['language']

    return question, translation, language


def choose_options(translation: str, question_language: str) -> tuple[list[str], int]:
    """Return a randomly chosen answer options"""

    def get_random_word(language):
        word_list = Translation.en_word_dict.keys() if language == 'russian' else Translation.ru_word_dict.keys()
        return random.choice(list(word_list))

    options = [get_random_word(question_language) for _ in range(3)]
    options.append(translation)
    random.shuffle(options)
    right_option_index = options.index(translation)
    return options, right_option_index
