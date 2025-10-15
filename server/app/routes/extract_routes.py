from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from ..schemas.models import ExtractRequest
from ..services.extractor_service import extract_articles

bp = Blueprint("extract", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp.post("/extract")
@swag_from({
    "tags": ["extract"],
    "summary": "Fetch and preprocess news articles",
    "description": "Fetches articles from configured news API and preprocesses text (clean, tokenize, lemmatize).",
    "requestBody": {
        "required": False,
        "content": {
            "application/json": {
                "schema": ExtractRequest.schema()
            }
        }
    },
    "responses": {
        200: {
            "description": "List of processed articles",
        },
        400: {"description": "Validation error"},
        500: {"description": "Server error"}
    }
})
def extract_handler():
    try:
        payload = request.get_json(silent=True) or {}
        req = ExtractRequest(**payload)
        articles = extract_articles(domains=req.domains, from_date=req.from_date)
        return jsonify({"count": len(articles), "items": articles}), 200
    except Exception as exc:  # noqa: BLE001
        logger.exception("/extract failed")
        return jsonify({"error": str(exc)}), 500
