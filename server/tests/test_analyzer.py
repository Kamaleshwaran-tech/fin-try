import pytest

from app.services.analyzer_service import get_analyzer


def test_vader_analyze_texts_basic():
    analyzer = get_analyzer()
    results = analyzer.analyze_texts(["I love this", "This is terrible"])
    assert len(results) == 2
    assert all("scores" in r for r in results)
    labels = [r["label"] for r in results]
    assert 1 in labels and -1 in labels


def test_keywords_extraction():
    analyzer = get_analyzer()
    kws = analyzer.extract_keywords(["Apple launches new iPhone", "Apple and Google partner"])
    assert isinstance(kws, list)
    assert len(kws) > 0
