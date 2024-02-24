import random
from translations.translation import Translation


def choose_ru_question() -> tuple[str, str]:
    """Returns a randomly chosen ru question and en translation"""
    question = random.choices(list(Translation.ru_word_dict.keys()), k=1)[0]
    translation = Translation.ru_word_dict[question]

    return question, translation
