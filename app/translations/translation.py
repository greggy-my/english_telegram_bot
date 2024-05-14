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
                split_words = word.split()
                if ' ' in split_words:
                    split_words.append(' ')
                for split_word in split_words:
                    split_word = split_word.lower()
                    if split_word in hash_dict:
                        hash_dict[split_word].append(word)
                    else:
                        hash_dict[split_word] = [word]

        # Processing Russian list
        process_words(cls.ru_word_dict.keys(), cls.ru_hash_dict)

        # Processing English list
        process_words(cls.en_word_dict.keys(), cls.en_hash_dict)


if __name__ == '__main__':
    Translation.instantiate_from_excel()
    print(len(Translation.ru_hash_dict))