from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pandas as pd
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

from ..core.config import get_settings
from .db import insert_many

# Ensure NLTK resources are available
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


def _clean_text(text: str) -> str:
    """Normalize a text string for analysis.

    Performs lowercasing, contraction expansion, punctuation/whitespace
    cleanup, ASCII stripping, and alphanumeric filtering.
    """
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = text.replace('(ap)', '')
    text = re.sub(r"\'s", " is ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r"\\", "", text)
    text = re.sub(r"\'", "", text)
    text = re.sub(r'\"', '', text)
    text = re.sub('[^a-zA-Z ?!]+', '', text)
    text = "".join(i for i in text if ord(i) < 128)
    return text.strip()


tokenizer = RegexpTokenizer(r"\w+")
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
stop_words.update(['char', 'u', 'hindustan', 'doj', 'washington'])


def _tokenize(text: str) -> List[str]:
    return tokenizer.tokenize(text)


def _remove_stopwords(tokens: List[str]) -> List[str]:
    return [w for w in tokens if w not in stop_words]


def _lemmatize(tokens: List[str]) -> str:
    return ' '.join([lemmatizer.lemmatize(word) for word in tokens])


def _normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning, tokenization, stopword removal and lemmatization."""
    df['combined_text'] = df['title'].map(str) + ' ' + df['content'].map(str)
    df['combined_text'] = df['combined_text'].map(_clean_text)
    df['tokens'] = df['combined_text'].map(_tokenize)
    df['tokens'] = df['tokens'].map(_remove_stopwords)
    df['lems'] = df['tokens'].map(_lemmatize)
    df.dropna(inplace=True)
    df['pub_date'] = pd.to_datetime(df['pub_date']).apply(lambda x: x.date())
    df['source'] = df['source'].apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else None)
    return df


def _articles_from_api_response(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for it in items:
        results.append({
            'title': it.get('title'),
            'author': it.get('author'),
            'source': it.get('source'),
            'description': it.get('description'),
            'content': it.get('content'),
            'pub_date': it.get('publishedAt'),
            'url': it.get('url'),
            'photo_url': it.get('urlToImage'),
        })
    return results


def extract_articles(domains: List[str] | None = None, from_date: str | None = None) -> List[Dict[str, Any]]:
    """Fetch news articles, preprocess text, persist, and return records.

    Persistence includes MongoDB `DailyNews` and a dated CSV in `assets/`.
    """
    settings = get_settings()
    news_url = settings.url
    api_key = settings.api_key
    if not news_url or not api_key:
        raise ValueError("URL and API_KEY must be configured")

    if not from_date:
        from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    domains = domains or settings.default_domains_list

    frames: List[pd.DataFrame] = []
    for domain in domains:
        params = {
            'domains': domain,
            'sortBy': 'popularity',
            'pageSize': 100,
            'apiKey': api_key,
            'language': 'en',
            'from': from_date,
        }
        response = requests.get(news_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        items = data.get('articles', [])
        frames.append(pd.DataFrame(_articles_from_api_response(items)))

    df = pd.concat(frames, ignore_index=True)
    df = _normalize_frame(df)

    # Persist to db and csv
    records = df.to_dict('records')
    insert_many("DailyNews", records)

    csv_dir = os.path.join('assets')
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, f"{from_date}.csv")
    df.to_csv(csv_path, index=False)

    return records
