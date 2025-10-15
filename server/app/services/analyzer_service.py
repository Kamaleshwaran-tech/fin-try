from __future__ import annotations

from typing import List, Dict, Any

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from ..core.config import get_settings
from .db import insert_many, fetch_collection

# Ensure NLTK resources are available
nltk.download('vader_lexicon')


class VaderAnalyzer:
    """VADER sentiment analyzer wrapper.

    Provides sentiment scoring, simple label mapping, and lightweight
    keyword extraction to support API endpoints.
    """

    def __init__(self) -> None:
        self._sia = SIA()

    def analyze_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Score multiple texts using VADER.

        Args:
            texts: List of input strings to analyze.

        Returns:
            List of dicts with text, scores, label, and word count.
        """
        results: List[Dict[str, Any]] = []
        for text in texts:
            pol_score = self._sia.polarity_scores(text or "")
            label = 0
            if pol_score['compound'] > 0.2:
                label = 1
            elif pol_score['compound'] < -0.2:
                label = -1
            results.append({
                "text": text,
                "scores": pol_score,
                "label": label,
                "word_count": len((text or "").split()),
            })
        return results

    def extract_keywords(self, texts: List[str], top_k: int = 20) -> List[str]:
        """Naive keyword extraction from input texts.

        Uses simple frequency of alpha tokens length>=3. This is fast
        and dependency-light; swap with RAKE/KeyBERT if needed later.
        """
        import re
        from collections import Counter

        tokens: List[str] = []
        for text in texts:
            for tok in re.findall(r"[a-zA-Z]{3,}", text.lower()):
                tokens.append(tok)
        return [w for w, _ in Counter(tokens).most_common(top_k)]


def get_analyzer() -> VaderAnalyzer:
    # For future: branch on settings.analyzer_model
    return VaderAnalyzer()
