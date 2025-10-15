import pytest

from app.services.extractor_service import _clean_text


def test_clean_text_normalizes_and_strips():
    text = "What's NEW???   I'm happy!!!\n"
    out = _clean_text(text)
    assert "what is" in out
    assert "i am" in out
    assert "?" not in out
    assert out.strip() == out
