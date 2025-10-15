"""Blueprint registration."""
from __future__ import annotations

from flask import Flask

from .extract_routes import bp as extract_bp
from .analyze_routes import bp as analyze_bp
from .visualize_routes import bp as visualize_bp
from .report_routes import bp as report_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(extract_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(visualize_bp)
    app.register_blueprint(report_bp)
