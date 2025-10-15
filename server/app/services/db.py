from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from pymongo import MongoClient, server_api

from ..core.config import get_settings


@dataclass
class MongoConfig:
    """Mongo connection parameters."""
    username: Optional[str]
    password: Optional[str]
    db_name: Optional[str]


def _mongo_uri(cfg: MongoConfig) -> str:
    """Build MongoDB URI from settings.

    Note: cluster host is fixed here to match the original project.
    """
    if not cfg.username or not cfg.password or not cfg.db_name:
        raise ValueError("Mongo credentials are not configured")
    username = quote_plus(cfg.username)
    password = quote_plus(cfg.password)
    return (
        f"mongodb+srv://{username}:{password}@news-analyzer.0ittn.mongodb.net/"
        f"{cfg.db_name}?retryWrites=true&w=majority&appName=News-analyzer"
    )


def get_mongo_client() -> MongoClient:
    """Return a MongoClient using environment configuration."""
    settings = get_settings()
    cfg = MongoConfig(
        username=settings.mongo_username,
        password=settings.mongo_password,
        db_name=settings.db_name,
    )
    uri = _mongo_uri(cfg)
    client = MongoClient(uri, server_api=server_api.ServerApi("1"))
    return client


def fetch_collection(collection_name: str, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
    """Fetch all documents from a collection as dicts."""
    client = get_mongo_client()
    db = client[get_settings().db_name]
    coll = db[collection_name]
    projection = projection or {"_id": 0}
    return list(coll.find({}, projection))


def insert_many(collection_name: str, records: List[Dict[str, Any]]) -> int:
    """Insert many records and return count inserted."""
    if not records:
        return 0
    client = get_mongo_client()
    db = client[get_settings().db_name]
    coll = db[collection_name]
    result = coll.insert_many(records)
    return len(result.inserted_ids)
