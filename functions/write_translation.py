import random
from translations.translation import Translation


async def choose_question() -> tuple[str, str, str]:
    """Returns a randomly chosen question"""

    language_choice = random.randint(0, 1)

    options_mapping = {
            0: {'language': 'russian', 'dict': Translation.ru_word_dict},
            1: {'language': 'english', 'dict': Translation.en_word_dict}
    }

    choice_map = options_mapping[language_choice]
    question = random.choices(list(choice_map['dict'].keys()), k=1)[0]
    translation = choice_map['dict'][question]
    language = choice_map['language']

    return question, translation, language
