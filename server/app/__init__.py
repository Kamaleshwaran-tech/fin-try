"""Flask application factory and extensions initialization."""
from __future__ import annotations

import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from .core.config import get_settings
from .core.logging import configure_logging
from .routes import register_blueprints


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Configured Flask app instance.
    """
    settings = get_settings()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key

    # CORS
    CORS(app, resources={r"/*": {"origins": settings.allowed_origins}})

    # Logging
    configure_logging(settings.log_level)

    # Swagger / OpenAPI setup
    app.config["SWAGGER"] = {
        "title": "News Analyzer API",
        "uiversion": 3,
    }
    Swagger(app)

    # Blueprints
    register_blueprints(app)

    @app.get("/health")
    def health():  # pragma: no cover
        return {"status": "ok"}

    return app
