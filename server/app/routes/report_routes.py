from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from ..schemas.models import SendReportRequest
from ..services.email_service import send_report

bp = Blueprint("report", __name__, url_prefix="")
logger = logging.getLogger(__name__)


@bp.post("/send-report")
@swag_from({
    "tags": ["report"],
    "summary": "Send analysis report via email",
    "description": "Triggers email sending using configured SMTP credentials.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": SendReportRequest.schema()
            }
        }
    },
    "responses": {
        200: {"description": "Report sent"},
        400: {"description": "Validation error"},
        500: {"description": "Server error"}
    }
})
def send_report_handler():
    try:
        payload = request.get_json(force=True)
        req = SendReportRequest(**payload)
        send_report(to_emails=req.to, subject=req.subject, body=req.body, attachments=req.attachments)
        return jsonify({"status": "sent"}), 200
    except Exception as exc:  # noqa: BLE001
        logger.exception("/send-report failed")
        return jsonify({"error": str(exc)}), 500
