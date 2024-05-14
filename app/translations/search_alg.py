import re

from fuzzywuzzy import fuzz

from app.translations.text_processing import TextProcessor
from app.translations.translation import Translation


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
        if ' ' == query[0]:
            query_words.insert(0, ' ')

        search_results = []
        for key in hash_dict.keys():
            if query_words[0] in key:
                for string in hash_dict[key]:
                    similarity_score = fuzz.partial_ratio(query, string.lower())
                    search_results.append((key, similarity_score))

        # Sort the results by similarity score in descending order
        search_results.sort(key=lambda x: x[1], reverse=True)
        if len(search_results) == 0:
            result = (None, None)
        else:
            chosen_key, similarity = search_results[0]
            chosen_translation = world_dict[chosen_key]
            result = (chosen_key, chosen_translation)
        return result


if __name__ == '__main__':
    Translation.instantiate_from_excel()
    print(Translation.ru_hash_dict)
    print(HashSearch.search(query='done'))