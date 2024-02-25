import random
from translations.translation import Translation


def choose_ru_question(chosen_unit: str) -> tuple[str, str]:
    """Returns a randomly chosen ru question and en translation"""
    if chosen_unit is not None:
        ru_list = list(filter(lambda x: f'{chosen_unit}_' in x, Translation.ru_list))
    else:
        ru_list = Translation.ru_list
    choice = random.choices(ru_list, k=1)[0]
    question = choice.split('_')[1]
    translation = Translation.ru_word_dict[question]

    return question, translation
