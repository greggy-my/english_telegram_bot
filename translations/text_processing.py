from math import sqrt, pow, exp
import numpy as np


class TextProcessor:

    @classmethod
    def text_to_numbers(cls, text: str, language: str) -> tuple:
        """Returns a vector representation of a string based on letters"""
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
                vector_positions[letter_vectors[letter]] += 1 / (1 + exp(2 * index))
        final_vector = tuple(vector_counts + vector_positions)
        return final_vector

    @classmethod
    def detect_text_language(cls, text: str) -> str:
        """Returns a language of a string (russian and english)"""
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

    @classmethod
    def cosine_similarity(cls, vector1: tuple, vector2: tuple) -> float:
        """Returns the cosine similarity between two vectors"""

        vector1 = list(vector1)
        vector2 = list(vector2)

        dot_product = 0
        magnitude_vector1 = 0
        magnitude_vector2 = 0
        vector1_length = len(vector1)
        vector2_length = len(vector2)

        if vector1_length == 0 or vector2_length == 0:
            return 0

        if vector1_length > vector2_length:
            vector2 = vector2 + [0] * (vector1_length - vector2_length)
        elif vector2_length > vector1_length:
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

        similarity = dot_product / magnitude

        # return cosine similarity
        return similarity
