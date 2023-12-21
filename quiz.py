import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from collections import defaultdict


async def choose_question(user_id: int,
                          users_progress_weights_en: defaultdict,
                          users_progress_weights_ru: defaultdict,
                          ru_word_dict: defaultdict, en_word_dict: defaultdict) -> tuple[str, str, str]:
    """Returns a randomly chosen question"""

    language_choice = random.randint(0, 1)

    options_mapping = {
            0: {'user_progress': users_progress_weights_ru, 'language': 'russian', 'dict': ru_word_dict},
            1: {'user_progress': users_progress_weights_en, 'language': 'english', 'dict': en_word_dict}
    }

    choice_map = options_mapping[language_choice]
    questions = []
    weights = []

    for question, weight in choice_map['user_progress'][user_id].items():
        questions.append(question)
        weights.append(weight)

    question = random.choices(questions, weights=weights, k=1)[0]

    translation = choice_map['dict'][question]
    language = choice_map['language']

    return question, translation, language


async def choose_extra_info(ru_word_dict_long: defaultdict, en_word_dict_long: defaultdict) -> tuple[str, str, str]:
    """Returns a randomly extra info"""

    language_choice = random.randint(0, 1)

    options_mapping = {
            0: {'language': 'russian', 'dict': ru_word_dict_long},
            1: {'language': 'english', 'dict': en_word_dict_long}
    }

    choice_map = options_mapping[language_choice]

    question = random.choices(list(choice_map['dict'].keys()))[0]

    translation = choice_map['dict'][question]
    language = choice_map['language']

    return question, translation, language


async def choose_options(question: str,
                         ru_word_dict: defaultdict, en_word_dict: defaultdict,
                         question_language: str) -> list[str]:
    """Return a randomly chosen answer options"""

    def get_random_word(language):
        word_list = en_word_dict.keys() if language == 'russian' else ru_word_dict.keys()
        return random.choice(list(word_list))

    options = []

    while len(options) < 3:
        option = get_random_word(question_language)
        if len(option.encode('utf-8')) < 62:
            options.append(option)

    word_dict = ru_word_dict if question_language == 'russian' else en_word_dict
    options.append(word_dict[question])

    random.shuffle(options)
    return options


async def inline_builder(question: str, question_language: str,
                         ru_word_dict: defaultdict, en_word_dict: defaultdict,
                         ) -> InlineKeyboardBuilder:
    """Return an InlineKeyboardBuilder based on a chosen question and options"""
    options = await choose_options(question=question, question_language=question_language,
                                   ru_word_dict=ru_word_dict, en_word_dict=en_word_dict)

    # Preparing new buttons
    buttons = []
    for option in options:
        buttons.append(InlineKeyboardButton(text=option, callback_data=option))

    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    builder = InlineKeyboardBuilder.from_markup(markup)

    builder.adjust(1, 1, 1, 1)

    return builder

