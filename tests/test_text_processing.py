import pytest
from contextlib import nullcontext as does_not_raise

from app.translations.text_processing import TextProcessor

@pytest.mark.parametrize(
    "query, result, expectation",
    [
        ("Hi", "english", does_not_raise()),
        ("Привет", "russian", does_not_raise()),
        ("№.,:;@", None, does_not_raise()),
        (1, None, pytest.raises(AttributeError))
    ]
)
def test_detect_language(query, result, expectation):
    with expectation:
        assert result == TextProcessor.detect_text_language(query)