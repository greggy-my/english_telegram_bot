from collections import defaultdict
from math import sqrt, pow, exp
from typing import Any, Generator, Tuple
from spacy.language import Language
from spacy_language_detection import LanguageDetector
import spacy
import copy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
import nltk
from Levenshtein import distance
import re


english_words = [
    "to categorise into/fall into groups",
    "content and process theories",
    "to discuss sth in term of",
    "Maslow’s Hierarchy of needs",
    "to fulfill/ satisfy needs",
    "physiological needs",
    "Herzsberg’s Two factor theory",
    "motivators and hygiene factors",
    "Three needs theory",
    "a need for achievement, affiliation, power",
    "to set/ tailor motivational targets to sb",
    "McGregor’s Theory X and Theory Y",
    "to be intrinsically lazy ≠ to be ambitious",
    "to build systems of control and supervision ≠ to provide the right conditions",
    "ERG (existence, relatedness, growth needs) theory",
    "Mayo’s Motivation theory",
    "norms and group cohesiveness factors",
    "Adam’s Equity theory",
    "fair treatment relative to others",
    "Vroom’s Expectancy theory",
    "Expectancy (effort), instrumentality (performance), valence (reward) factors",
    "The higher the result, the higher the motivation.",
    "Taylor’s Scientific management",
    "principles to maximize efficiency",
    "to monitor workers closely to avoid slacking off",
    "Self-efficacy theory of motivation (task specific theory)",
    "experience, vicarious experience, social persuasion, physiological feedback factors",
    "Skinner’s Reinforcement theory of motivation",
    "positive and negative reinforcement, punishment, extinction factors",
    "Lock’s Goal setting theory",
    "to be based on the premise",
    "to set right goals (clarity, challenge, commitment, feedback, task complexity)",
    "to allow for sth",
    "to slack off"
]

russian_translations = [
    "распределять по группам",
    "теории содержания и процесса",
    "обсуждать что-либо в терминах",
    "Иерархия потребностей Маслоу",
    "удовлетворение потребностей",
    "физиологические потребности в ...",
    "Двухфакторная теория Херцсбера",
    "мотиваторы и гигиенические факторы",
    "Теория трех потребностей",
    "потребность в достижении, принадлежности, власти",
    "постановка/настройка мотивационных целей для кого-либо",
    "Теория X и Y МакГрегора",
    "быть внутренне ленивым ≠ быть амбициозным",
    "создание систем контроля и надзора ≠ создание необходимых условий",
    "Теория ERG (потребности в существовании, родстве, росте)",
    "теория мотивации Мэйо",
    "нормы и факторы групповой сплоченности",
    "Теория справедливости Адама",
    "справедливое отношение к другим",
    "Теория ожиданий Врума",
    "факторы ожидаемости (усилия), инструментальности (результаты), валентности (вознаграждение)",
    "чем выше результат, тем выше мотивация.",
    "научный менеджмент Тейлора",
    "принципы максимизации эффективности",
    "тщательный контроль за работниками во избежание халтуры",
    "теория самоэффективности мотивации (теория, ориентированная на конкретную задачу)",
    "опыт, …, социальное убеждение, физиологические факторы обратной связи",
    "Теория мотивации с подкреплением Скиннера",
    "положительные и отрицательное подкрепление, наказание, факторы угасания",
    "Теория целеполагания Локка",
    "основывается на предпосылке",
    "ставить правильные цели (ясность, вызов, приверженность, обратная связь, сложность задачи)",
    "учесть что-то; допускать что-либо",
    "ослаблять"
]

english_words_2 = [
    "Tech unicorn",
    "to accomplish a (shared) goal",
    "to change over time",
    "to make/ pursue a career",
    "career path/ longevity/ development/ opportunities/ breaks/ ladder etc",
    "to build a pension",
    "trading salary for equity",
    "to be/ stay in the game = actively participating in something",
    "to give/ get recognition for sth",
    "to de-prioritise recognition",
    "to look for experiences beyond work",
    "to personalise goals, measurement, incentives",
    "to spread incentives across employees",
    "a thing of the past",
    "a decent salary/ wage/standard of living etc",
    "to remind sb of sth",
    "to turn to sth",
    "to remind sh of sth",
    "To roll up one's sleeves",
    "To get one's hands dirty",
    "To treat sb like a cog in a machine",
    "to create a collaborative environment",
    "to do sth time and again",
    "to feel valued ≠ to be unheard, undervalued",
    "to share one's vision with the team",
    "the big picture = the situation as a whole",
    "to overlook the big picture",
    "big picture thinking",
    "to be part of the big picture process",
    "to give positive, specific, genuine feedback",
    "to earn/ give a praise",
    "to compliment sb on their work",
    "to pinpoint what/how/ why etc",
    "to pinpoint approaches and strategies",
    "to lead by example",
    "to allow for/ encourage personal development opportunities"
]

# Переводы на русском
russian_translations_2 = [
    "технологический единорог",
    "достижение общей цели",
    "изменяться в течение времени",
    "строить карьеру",
    "карьерный путь/долголетие/развитие/возможности/перерывы/лестница",
    "формировать пенсию",
    "обмен зарплаты на акции",
    "оставаться в игре = активно участвовать в чем-либо",
    "получить признание за что-либо",
    "отдать предпочтение признанию",
    "искать опыт вне работы",
    "персонализировать цели, измерения, стимулы",
    "распределять стимулы между сотрудниками",
    "дело прошлого",
    "достойная зарплата/оклад/уровень жизни",
    "напомнить кому-либо о чем-либо",
    "перейти к чему-то",
    "напоминать о чем-либо",
    "замять рукава",
    "умазаться",
    "рассматривать кого-то как зубчик в механизме",
    "создавать условия для совместной работы",
    "делать что-то снова и снова",
    "чувствовать себя оцененным ≠ быть неуслышанным, недооцененным",
    "делиться своим видением с командой",
    "общая картина = ситуация в целом",
    "упускать из виду общую картину",
    "мышление большая картина ?? широкое видение",
    "быть частью процесса создания общей картины",
    "давать позитивную, конкретную, искреннюю обратную связь",
    "заслужить/похвалить",
    "похвалить кого-то за работу",
    "точно определить, что/как/почему",
    "определять подходы и стратегии",
    "подавать пример",
    "предоставлять/поощрять возможности для личного развития"
]

english_words_3 = [
    "Honest day's pay for an honest day's work.",
    "to work side-by-side (with sb)",
    "to bring sb (the team) together in doing sth",
    "to value job titles/ professional development/ expertise/ opportunities to grow etc",
    "to be well-established in one's career",
    "to hold positions of power and authority",
    "to apply for the position of",
    "to prefer (enjoy) monetary/ nonmonetary/ social/ experiential etc rewards",
    "to require/ receive constant/ immediate etc feedback",
    "flexible retirement planning",
    "recognition from the boss/ peer recognition",
    "a work-centric/ goal-oriented/ the ME/ the ME-ME-ME (melenious) / tech-savvy etc generation",
    "levels of responsibility",
    "perks and privileges",
    "stock option",
    "to be credited for doing sth",
    "to see sth first-hand = If you experience something first-hand, you experience it yourself.",
    "to get promotion - to be promoted by rank/ age/ seniority etc",
    "promotions based on competence",
    "mentor - mentoring – mentorship",
    "to come into your own = to be very useful or successful in a particular situation",
    "to sell one's skills to the highest bidder",
    "to jump from one organisation to another",
    "job-hopping",
    "to embrace the latest technology",
    "to demand flexible schedules",
    "to expect structure, clear directions, and transparency"
]

# Переводы на русском
russian_translations_3 = [
    "честная плата за честный день работы",
    "работать бок о бок (с кем-либо)",
    "объединять кого-либо для выполнения чего-либо",
    "ценить должность/профессиональное развитие/опыт/возможности роста",
    "зарекомендовать себя в чем-то",
    "занимать властные и авторитетные позиции",
    "претендовать на должность",
    "предпочитать (получать) денежное/неденежное/социальное/экспериментальное вознаграждение",
    "требовать/получать постоянную/незамедлительную обратную связь",
    "гибкое планирование выхода на пенсию",
    "признание со стороны начальника/признание со стороны коллег",
    "поколение, ориентированное на работу/цели/технически подкованное",
    "уровень ответственности",
    "льготы и привилегии",
    "акционерный опцион",
    "получить похвалу за что-либо; быть признанным в чем-то",
    "видеть что-либо воочию",
    "быть повышенным в звании/возрасте/стаже",
    "продвижение по службе на основе компетентности",
    "ментор – наставник – менторство",
    "раскрыть весь свой потенциал = быть очень полезным или успешным в определенной ситуации",
    "продавать свои навыки тому, кто больше заплатит",
    "переходить из одной организации в другую",
    "частая смена работы",
    "использовать новейшие технологии",
    "требовать гибкий график",
    "ожидать структурированности, четких указаний и прозрачности"
]

english_words_4 = [
    "Over the horizon (idiom) - coming in the near future",
    "Just around the corner (idiom) - not far away, or going to happen soon",
    "Jumb out (idiom) - To become numb io one's emotions or ouside sensations as a resuli some",
    "Don't let that noise knock you off course!",
    "wealth and fame",
    "to find one's sense of completion",
    "to free people from concern",
    "to talk/ learn/ speak etc from experience",
    "to be interrelated = to be bound together (into a single garment of destiny)",
    "to take a stand for/against",
    "to fix a problem/ an injustice",
    "to live in service to humanity",
    "to rot and fall apart",
    "to stand in the way of sth",
    "to tear someone apart",
    "to push ahead with sth",
    "to figure out",
    "to reach out (to sb)",
    "To tick the (right) boxes - to satisfy or fulfill everything that is necessary or desired.",
    "to re-engage interest",
    "to underscore the need for",
    "employee commitment",
    "be a catalyst for doing sth",
    "to accelerate the move to digitization",
    "digital natives",
    "to be steeped in sth",
    "to have meaningful substantive roles",
    "to have a seat in the boardroom",
    "the company's legacy",
    "operational management",
    "relieve the burden of operational management",
    "to spawn shifts",
    "to play a hands-off role",
    "supervisor - supervisee",
    "to micromanage",
    "Praise in public, correct in private.",
    "public humiliation",
    "low morale of the employees/ at work",
    "to complain - a complaint",
    "to promise a pay rise",
    "to move to a better paid position",
    "to regain motivation",
    "to work out mutually beneficial solutions",
    "determination (n)",
    "perseverance (n)",
    "tenacity (n)",
    "endurance (n)",
    "enthusiasm",
    "to act in a cheerful spirit of cooperation",
    "to instigate",
    "Drive-reduction theory primary/ secondary drive",
    "impetus (n) for sth/ to do sth",
    "urge (n)",
    "provocation (n)"
]

# Переводы на русском
russian_translations_4 = [
    "за горизонтом (в ближайшем будущем)",
    "за поворотом",
    "онеметь, остолбенеть (физическое и душевное)",
    "Не сбиться с пути!",
    "богатство и слава",
    "обрести чувство завершенности",
    "освободить людей от забот, беспокойства",
    "говорить / учиться / говорить и т.д. на основе опыта",
    "быть взаимосвязанным = быть связанным вместе (в единое одеяние судьбы)",
    "занять позицию твердую и решительную",
    "исправить проблему/ несправедливость",
    "жить, служа человечеству",
    "гнить и разрушаться",
    "стоять на пути чего-л./мешать",
    "разрывать кого-либо на части (изнутри)",
    "продвигаться, не смотря на сопротивление",
    "выяснять",
    "обращаться (к кому-л.); помогать",
    "удовлетворять или выполнять все необходимое или желаемое.",
    "вновь вызвать интерес",
    "подчеркнуть необходимость",
    "приверженность сотрудников",
    "быть катализатором чего-л.",
    "ускорить переход к цифровым технологиям",
    "цифровые жители",
    "быть погруженным во что-л.",
    "играть значимую содержательную роль",
    "иметь место в зале заседаний совета директоров",
    "наследие компании",
    "оперативное управление",
    "облегчить бремя оперативного управления",
    "порождать смены",
    "играть роль 'свободной руки'",
    "руководитель - подчиненный",
    "контролировать каждый шаг",
    "Хвалить на людях, исправлять наедине.",
    "публичное унижение",
    "низкий моральный дух сотрудников / на работе",
    "жаловаться/жалоба",
    "обещать повышение зарплаты",
    "перевести на более высокооплачиваемую должность",
    "восстановить мотивацию",
    "выработать взаимовыгодные решения",
    "решительность",
    "упорство",
    "упорный противник",
    "выносливость",
    "быть испытанием на выносливость человека",
    "энтузиазм",
    "действовать в бодром духе сотрудничества",
    "подстрекать",
    "Теория редукции привода первичный/вторичный привод",
    "импульс (n) для чего-л. или для выполнения чего-л.",
    "стремление, порыв",
    "провокация"
]


def create_lists():
    en_list = []
    ru_list = []

    en_list.extend(english_words)
    en_list.extend(english_words_2)
    en_list.extend(english_words_3)
    en_list.extend(english_words_4)

    ru_list.extend(russian_translations)
    ru_list.extend(russian_translations_2)
    ru_list.extend(russian_translations_3)
    ru_list.extend(russian_translations_4)

    return ru_list, en_list


def create_word_dicts(ru_list: list, en_list: list) -> tuple[defaultdict, defaultdict]:
    # Создаем словарь с соответствиями слов и переводов
    ru_word_dict = defaultdict(lambda: None, zip(ru_list, en_list))
    en_word_dict = defaultdict(lambda: None, zip(en_list, ru_list))

    return ru_word_dict, en_word_dict


def detect_text_language(text: str) -> str:
    """Returns a string with a language of a message"""
    # Define character sets for different languages
    russian_chars = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
    english_chars = set("abcdefghijklmnopqrstuvwxyz")

    # Count the number of characters in each set
    num_russian_chars = sum(1 for char in text.lower() if char in russian_chars)
    num_english_chars = sum(1 for char in text.lower() if char in english_chars)

    # Compare the counts to determine the language
    if num_russian_chars > num_english_chars:
        return "russian"
    elif num_english_chars > num_russian_chars:
        return "english"
    else:
        return "Unknown"


# def text_to_numbers(text: str, language: str) -> tuple:
#     """
#     Convert text to numbers character by character based on ASCII values.
#
#     Parameters:
#     - text (str): The input text to be converted.
#     - language (str): The language of the text ('english' or 'russian').
#
#     Returns:
#     - list: A list of numbers representing the text character by character.
#     """
#     if language == 'russian':
#         base_value = ord('а')  # Unicode code point of the first Russian letter 'а'
#     else:
#         base_value = ord('a')  # Unicode code point of the first English letter 'a'
#
#     numbers = tuple(ord(char) - base_value for char in text.lower())
#     return numbers


def text_to_numbers(text: str, language: str) -> tuple:

    if language == 'russian':
        alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        letter_vectors = {letter: i for i, letter in enumerate(alphabet)}
    else:
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        letter_vectors = {letter: i for i, letter in enumerate(alphabet)}

    vector_counts = np.zeros(len(alphabet))
    vector_positions = np.zeros(len(alphabet))

    # Count the occurrences of each letter in the word
    for index, letter in enumerate(text.lower()):
        if letter in alphabet:
            vector_counts[letter_vectors[letter]] += 0.1
            vector_positions[letter_vectors[letter]] += 1/(1 + exp(index))
    final_vector = tuple(vector_counts+vector_positions)
    return final_vector


def cosine_similarity(vector1: list, vector2: list) -> float:
    """Returns the cosine of the angle between two vectors."""
    dot_product = 0
    magnitude_vector1 = 0
    magnitude_vector2 = 0
    vector1_length = len(vector1)
    vector2_length = len(vector2)

    if vector1_length == 0 or vector2_length == 0:
        return 0

    if vector1_length > vector2_length:
        # fill vector2 with 0s until it is the same length as vector1 (required for dot product)
        # vector1 = vector1[:vector2_length]
        vector2 = vector2 + [0] * (vector1_length - vector2_length)
    elif vector2_length > vector1_length:
        # fill vector1 with 0s until it is the same length as vector2 (required for dot product)
        # vector2 = vector2[:vector1_length]
        vector1 = vector1 + [0] * (vector2_length - vector1_length)

    # dot product calculation
    for i in range(len(vector1)):
        dot_product += vector1[i] * vector2[i]

    # vector1 magnitude calculation
    for i in range(len(vector1)):
        magnitude_vector1 += pow(vector1[i], 2)

    # vector2 magnitude calculation
    for i in range(len(vector2)):
        magnitude_vector2 += pow(vector2[i], 2)

    # final magnitude calculation
    magnitude = sqrt(magnitude_vector1) * sqrt(magnitude_vector2)

    simialrity = dot_product / magnitude

    # return cosine similarity
    return simialrity


def create_embedding_dicts(ru_word_dict: dict, en_word_dict: dict) -> tuple[defaultdict, defaultdict]:
    ru_word_dict_numbers = defaultdict(lambda: None)
    for ru_word, en_word in ru_word_dict.items():
        new_key = text_to_numbers(ru_word, language="russian")
        ru_word_dict_numbers[new_key] = en_word

    en_word_dict_numbers = defaultdict(lambda: None)
    for en_word, ru_word in en_word_dict.items():
        new_key = text_to_numbers(en_word, language="english")
        en_word_dict_numbers[new_key] = ru_word

    return ru_word_dict_numbers, en_word_dict_numbers


def find_word(query: str, ru_word_dict_numbers:dict, ru_word_dict: dict, en_word_dict_numbers:dict, en_word_dict: dict)\
        -> tuple[str, str, list, list] | None:

    pattern = re.compile(r'^[a-zA-Zа-яА-Я]+$')
    if not bool(pattern.match(query)):
        return None, None
    ru_word_dict_numbers = copy.deepcopy(ru_word_dict_numbers)
    en_word_dict_numbers = copy.deepcopy(en_word_dict_numbers)
    ru_word_dict = copy.copy(ru_word_dict)
    en_word_dict = copy.copy(en_word_dict)
    language = detect_text_language(query)
    query = list(text_to_numbers(query, language=language))

    max_sim = -1
    if language == 'russian':
        for ru_word, en_word in ru_word_dict_numbers.items():
            key_array = list(ru_word)
            similarity = cosine_similarity(query, key_array)

            if similarity > max_sim:
                max_sim = similarity
                chosen_value = en_word
                chosen_key = en_word_dict[chosen_value]
                chosen_key_array = key_array

    elif language == 'english':
        for en_word, ru_word in en_word_dict_numbers.items():
            key_array = list(en_word)
            similarity = cosine_similarity(query, key_array)

            if similarity > max_sim:
                max_sim = similarity
                chosen_value = ru_word
                chosen_key = ru_word_dict[chosen_value]
                chosen_key_array = key_array
    else:
        return None, None

    print(query)
    print(chosen_key_array)

    return chosen_key, chosen_value


def find_word_levi(query: str, ru_word_dict_numbers:dict, ru_word_dict: dict, en_word_dict_numbers:dict, en_word_dict: dict)\
        -> tuple[str, str, list, list] | None:
    ru_word_dict_numbers = copy.deepcopy(ru_word_dict_numbers)
    en_word_dict_numbers = copy.deepcopy(en_word_dict_numbers)
    ru_word_dict = copy.copy(ru_word_dict)
    en_word_dict = copy.copy(en_word_dict)
    language = detect_text_language(query)

    max_sim = - 10
    if language == 'russian':
        for ru_word, en_word in ru_word_dict.items():
            similarity = 1 - (distance(query, ru_word)/max(len(query), len(ru_word)))

            if similarity > max_sim:
                max_sim = similarity
                chosen_key = ru_word
                chosen_value = en_word

    elif language == 'english':
        for en_word, ru_word in en_word_dict.items():
            similarity = 1 - (distance(query, en_word)/max(len(query), len(en_word)))

            if similarity > max_sim:
                max_sim = similarity
                chosen_key = en_word
                chosen_value = ru_word

    else:
        return None

    return chosen_key, chosen_value, query


if __name__ == "__main__":
    for i in range (5):
        ru_list, en_list = create_lists()
        ru_word_dict, en_word_dict = create_word_dicts(ru_list=ru_list, en_list=en_list)
        ru_word_dict_numbers, en_word_dict_numbers = create_embedding_dicts(ru_word_dict=ru_word_dict,
                                                                            en_word_dict=en_word_dict)
        print(find_word(query='endurance',
                  ru_word_dict=ru_word_dict,
                  en_word_dict=en_word_dict,
                  ru_word_dict_numbers=ru_word_dict_numbers,
                  en_word_dict_numbers=en_word_dict_numbers))

        print(find_word_levi(query='en',
                  ru_word_dict=ru_word_dict,
                  en_word_dict=en_word_dict,
                  ru_word_dict_numbers=ru_word_dict_numbers,
                  en_word_dict_numbers=en_word_dict_numbers))
