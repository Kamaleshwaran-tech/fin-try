from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from ..schemas.models import AnalyzeRequest
from ..services.analyzer_service import get_analyzer
from ..services.cache_service import append_mean_polarity_csv
from ..services.db import insert_many

bp = Blueprint("analyze", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp.post("/analyze")
@swag_from({
    "tags": ["analyze"],
    "summary": "Analyze sentiment for raw text or articles",
    "description": "Accepts raw text(s) or preprocessed articles and returns VADER-based sentiment with labels and optional keywords.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": AnalyzeRequest.schema()
            }
        }
    },
    "responses": {
        200: {"description": "Sentiment results"},
        400: {"description": "Validation error"},
        500: {"description": "Server error"}
    }
})
def analyze_handler():
    try:
        """Analyze sentiment for provided input and return results.

        Supports `text`, `texts`, or `articles` in the request body.
        Also appends mean polarity to CSV cache for daily tracking.
        """
        payload = request.get_json(force=True)
        req = AnalyzeRequest(**payload)
        analyzer = get_analyzer()
        if req.text:
            results = analyzer.analyze_texts([req.text])
        elif req.texts:
            results = analyzer.analyze_texts(req.texts)
        elif req.articles:
            texts = [a.combined_text or (a.title or "") + " " + (a.content or "") for a in req.articles]
            results = analyzer.analyze_texts(texts)
            # Persist to PolarityData with article metadata
            records_for_db = []
            for art, res in zip(req.articles, results):
                scores = res.get("scores", {})
                records_for_db.append({
                    "headline": res.get("text"),
                    "compound": scores.get("compound"),
                    "neg": scores.get("neg"),
                    "neu": scores.get("neu"),
                    "pos": scores.get("pos"),
                    "label": res.get("label"),
                    "title": art.title,
                    "author": art.author,
                    "source": art.source,
                    "description": art.description,
                    "pub_date": art.pub_date,
                })
            try:
                insert_many("PolarityData", records_for_db)
            except Exception:
                logger.exception("Failed to persist PolarityData")
        else:
            return jsonify({"error": "Provide one of: text, texts, or articles"}), 400

        # Optional keywords
        keywords = analyzer.extract_keywords([r["text"] for r in results])
        # Cache mean polarity
        try:
            append_mean_polarity_csv(results)
        except Exception:  # cache errors should not break API
            logger.exception("Failed to append mean polarity cache")
        return jsonify({"count": len(results), "items": results, "keywords": keywords}), 200
    except Exception as exc:  # noqa: BLE001
        logger.exception("/analyze failed")
        return jsonify({"error": str(exc)}), 500
