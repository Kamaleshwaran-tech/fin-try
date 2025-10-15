from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from ..services.visualizer_service import get_visualization_payload

bp = Blueprint("visualize", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp.get("/visualize")
@swag_from({
    "tags": ["visualize"],
    "summary": "Get polarity and keyword trends",
    "description": "Returns aggregated polarity over time and top keywords for visualization.",
    "parameters": [
        {
            "name": "source",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": "Optional source filter"
        }
    ],
    "responses": {
        200: {"description": "Visualization data"},
        500: {"description": "Server error"}
    }
})
def visualize_handler():
    try:
        source = request.args.get("source")
        payload = get_visualization_payload(source=source)
        return jsonify(payload), 200
    except Exception as exc:  # noqa: BLE001
        logger.exception("/visualize failed")
        return jsonify({"error": str(exc)}), 500
