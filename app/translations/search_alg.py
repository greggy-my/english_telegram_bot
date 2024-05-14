import re

from fuzzywuzzy import fuzz
import Levenshtein
import difflib
import jellyfish

from app.translations.text_processing import TextProcessor
from app.translations.translation import Translation


def longest_common_substring(str1, str2):
    m = len(str1)
    n = len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    longest = 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                longest = max(longest, dp[i][j])
            else:
                dp[i][j] = 0
    return longest


def word_match_ratio(str1, str2):
    words1 = set(str1.split())
    words2 = set(str2.split())
    common_words = words1.intersection(words2)
    total_words = words1.union(words2)
    return len(common_words) / len(total_words) if total_words else 0


def calculate_similarity(query, potential_answer):
    # fuzzywuzzy ratios
    fuzz_partial_ratio = fuzz.partial_ratio(query, potential_answer)

    # jellyfish distances and ratios
    jaro_winkler_similarity = jellyfish.jaro_winkler_similarity(query, potential_answer)

    # Longest common substring ratio
    longest_common_substr_len = longest_common_substring(query, potential_answer)
    longest_common_substr_ratio = longest_common_substr_len / len(query)

    # Word match ratio
    word_match = word_match_ratio(query, potential_answer)

    # Combining all ratios
    combined_ratio = 0.25 * (fuzz_partial_ratio / 100) + 0.25 * jaro_winkler_similarity + \
                     0.25 * longest_common_substr_ratio + 0.25 * word_match

    return combined_ratio


class HashSearch:
    @classmethod
    def search(cls, query: str):

        """Returns the most similar result and probability"""
        if len(Translation.ru_hash_dict) == 0 or len(Translation.ru_word_dict) == 0:
            raise Exception('Empty Translation')

        if len(query) == 0 or query.isdigit():
            return None, None

        language = TextProcessor.detect_text_language(query)

        hash_dict = Translation.ru_hash_dict if language == 'russian' else Translation.en_hash_dict
        world_dict = Translation.ru_word_dict if language == 'russian' else Translation.en_word_dict

        query = query.lower()
        query = re.sub(r'[^a-zA-Zа-яА-Я ]', '', query)
        query_words = query.split()
        print(query)
        print(query_words)
        if ' ' == query[0]:
            query_words.insert(0, ' ')

        search_results = []
        for key in hash_dict.keys():
            if query_words[0] in key:
                for string in hash_dict[key]:
                    string = string.lower()
                    similarity_score = calculate_similarity(query, string)
                    search_results.append((string, similarity_score))

        # Sort the results by similarity score in descending order
        search_results.sort(key=lambda x: x[1], reverse=True)
        print(search_results)
        if len(search_results) == 0:
            result = (None, None)
        else:
            chosen_key, similarity = search_results[0]
            chosen_translation = world_dict[chosen_key]
            result = (chosen_key, chosen_translation)
        print(result)
        return result


if __name__ == '__main__':
    Translation.instantiate_from_excel()
    print(Translation.ru_hash_dict)
    print(HashSearch.search(query='done'))