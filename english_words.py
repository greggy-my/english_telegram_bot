import datetime
from collections import defaultdict
from math import sqrt, pow, exp
import copy
import numpy as np
import re
import pandas as pd
from fuzzywuzzy import fuzz
import asyncio


def create_lists():
    df = pd.read_excel('translation_pairs.xlsx')
    en_list = [s.lower().capitalize().replace('.', '') for s in df['en'].to_list()]
    ru_list = [s.lower().capitalize().replace('.', '') for s in df['ru'].to_list()]

    del df
    return ru_list, en_list


def create_word_dicts(ru_list: list, en_list: list) -> tuple[defaultdict, defaultdict, defaultdict, defaultdict]:
    # Создаем словарь с соответствиями слов и переводов
    ru_word_dict = defaultdict(lambda: None, zip(ru_list, en_list))
    en_word_dict = defaultdict(lambda: None, zip(en_list, ru_list))
    en_dict_ind = defaultdict(lambda: None, {value: index for index, value in enumerate(en_list)})
    ru_dict_ind = defaultdict(lambda: None, {value: index for index, value in enumerate(ru_list)})
    return ru_word_dict, en_word_dict, ru_dict_ind, en_dict_ind


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


def text_to_numbers(text: str, language: str) -> tuple:

    if language == 'russian':
        alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя "
        letter_vectors = {letter: i for i, letter in enumerate(alphabet)}
    else:
        alphabet = "abcdefghijklmnopqrstuvwxyz "
        letter_vectors = {letter: i for i, letter in enumerate(alphabet)}

    vector_counts = np.zeros(len(alphabet))
    vector_positions = np.zeros(len(alphabet))

    # Count the occurrences of each letter in the word
    for index, letter in enumerate(text.lower()):
        if letter in alphabet:
            vector_counts[letter_vectors[letter]] += 0
            vector_positions[letter_vectors[letter]] += 1 / (1 + exp(2*index))
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
    for i in range(vector1_length):
        dot_product += vector1[i] * vector2[i]

    # vector1 magnitude calculation
    for i in range(vector1_length):
        magnitude_vector1 += pow(vector1[i], 2)

    # vector2 magnitude calculation
    for i in range(vector2_length):
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


async def find_word(query: str, ru_word_dict_numbers:dict, ru_word_dict: dict, en_word_dict_numbers:dict, en_word_dict: dict)\
        -> tuple[str, str] | tuple[None, None]:

    pattern = re.compile(r'^[0-9!@#$%^&*()_+=\-[\]{};:\'",.<>?/\\|`~]+$')
    if bool(pattern.match(query)):
        return None, None
    ru_word_dict_numbers = copy.deepcopy(ru_word_dict_numbers)
    en_word_dict_numbers = copy.deepcopy(en_word_dict_numbers)
    ru_word_dict = copy.copy(ru_word_dict)
    en_word_dict = copy.copy(en_word_dict)
    language = detect_text_language(query)
    query = text_to_numbers(query, language=language)

    max_sim = -1
    if language == 'russian':
        for ru_word, en_word in ru_word_dict_numbers.items():
            key_array = ru_word
            similarity = cosine_similarity(query, key_array)

            if similarity > max_sim:
                max_sim = similarity
                chosen_value = en_word
                chosen_key = en_word_dict[chosen_value]

    elif language == 'english':
        for en_word, ru_word in en_word_dict_numbers.items():
            key_array = en_word
            similarity = cosine_similarity(query, key_array)

            if similarity > max_sim:
                max_sim = similarity
                chosen_value = ru_word
                chosen_key = ru_word_dict[chosen_value]
    else:
        return None, None

    return chosen_key, chosen_value


class StringSearch:
    def __init__(self, strings):
        self.string_dict = {}
        self.build_index(strings)

    def build_index(self, strings):
        for string in strings:
            words = string.split()
            if ' ' in string:
                words.append(' ')
            for word in words:
                word = word.lower()
                if word in self.string_dict:
                    self.string_dict[word].append(string)
                else:
                    self.string_dict[word] = [string]

    async def search(self, query):
        query = query.lower()
        query = re.sub(r'[^a-zA-Zа-яА-Я ]', '', query)
        query_words = query.split()
        if ' ' == query[0]:
            query_words.insert(0, ' ')
        results = []

        for key in self.string_dict.keys():
            if query_words[0] in key:
                for string in self.string_dict[key]:
                    similarity_score = fuzz.partial_ratio(query, string.lower())
                    results.append((string, similarity_score))

        # Sort the results by similarity score in descending order
        results.sort(key=lambda x: x[1], reverse=True)
        if len(results) == 0:
            result = (None, None)
        else:
            result = results[0]
        return result


async def find_word_hash(query: str,
                   ru_string_search: StringSearch,
                   en_string_search: StringSearch,
                   ru_word_dict: dict,
                   en_word_dict: dict) -> tuple[str, str] | tuple[None, None]:

    pattern = re.compile(r'^[0-9!@#$%^&*()_+=\-[\]{};:\'",.<>?/\\|`~]+$')
    if bool(pattern.match(query)):
        return None, None
    language = detect_text_language(query)

    if language == 'russian':
        chosen_key, similarity = await ru_string_search.search(query=query)
        chosen_translation = ru_word_dict[chosen_key]

    elif language == 'english':
        chosen_key, similarity = await en_string_search.search(query=query)
        chosen_translation = en_word_dict[chosen_key]

    else:
        return None, None

    return chosen_key, chosen_translation


if __name__ == "__main__":
    ru_list, en_list = create_lists()
    ru_word_dict, en_word_dict, ru_dict_ind, en_dict_ind = create_word_dicts(ru_list=ru_list, en_list=en_list)
    ru_word_dict_numbers, en_word_dict_numbers = create_embedding_dicts(ru_word_dict=ru_word_dict,
                                                                        en_word_dict=en_word_dict)
    ru_string_search = StringSearch(ru_list)
    en_string_search = StringSearch(en_list)

    async def main():
        print(await find_word(query='to ',
                              ru_word_dict=ru_word_dict,
                              en_word_dict=en_word_dict,
                              ru_word_dict_numbers=ru_word_dict_numbers,
                              en_word_dict_numbers=en_word_dict_numbers))

        print(await find_word_hash(query='mokey wrench',
                                   ru_word_dict=ru_word_dict,
                                   en_word_dict=en_word_dict,
                                   ru_string_search=ru_string_search,
                                   en_string_search=en_string_search))
    asyncio.run(main())


