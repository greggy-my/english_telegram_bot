
class TextProcessor:

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
