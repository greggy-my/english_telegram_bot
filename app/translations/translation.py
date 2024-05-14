import os
from collections import defaultdict

import pandas as pd


class Translation:
    units = set()

    ru_list = []
    en_list = []

    ru_word_dict = defaultdict()
    en_word_dict = defaultdict()

    ru_hash_dict = defaultdict(lambda: [])
    en_hash_dict = defaultdict(lambda: [])

    @classmethod
    def instantiate_from_excel(cls) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if 'translation_pairs.xlsx' in os.listdir(script_dir):
            translations_df = pd.read_excel(f'{script_dir}/translation_pairs.xlsx')
            for index, row in translations_df.iterrows():
                row_dict = row.to_dict()

                unit = str(row_dict.get('unit')).lower()
                russian_word = str(row_dict.get('ru')).lower()
                english_word = str(row_dict.get('en')).lower()
                assert isinstance(russian_word, str), f'Russian word {russian_word} is not str'
                assert isinstance(english_word, str), f'English word {english_word} is not str'

                cls.units.add(unit)
                cls.ru_list.append(f'{unit}_{russian_word}')
                cls.en_list.append(f'{unit}_{english_word}')
                cls.en_word_dict[english_word] = russian_word
                cls.ru_word_dict[russian_word] = english_word

            cls.build_hash_dict()
            cls.units = sorted(cls.units)

        else:
            raise Exception('No translations file')

    @classmethod
    def build_hash_dict(cls):
        """Builds a hash map of splited_words to strings based on the text population"""
        def process_words(lst, hash_dict):
            for word in lst:
                splitted_words = word.split()
                if ' ' in splitted_words:
                    splitted_words.append(' ')
                for splitted_word in splitted_words:
                    splitted_word = splitted_word.lower()
                    if word in hash_dict:
                        hash_dict[word].append(splitted_word)
                    else:
                        hash_dict[word] = [splitted_word]

        # Processing Russian list
        process_words(cls.ru_word_dict.keys(), cls.ru_hash_dict)

        # Processing English list
        process_words(cls.en_word_dict.keys(), cls.en_hash_dict)


if __name__ == '__main__':
    Translation.instantiate_from_excel()
    print(len(Translation.ru_hash_dict))