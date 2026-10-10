"""Cloud-Native DevSecOps & GitOps Delivery Platform — Flask application."""

from flask import Flask, jsonify


def create_app():
    """Application factory."""
    app = Flask(__name__)

    @app.get("/")
    def index():
        return jsonify(
            name="Cloud-Native DevSecOps & GitOps Delivery Platform",
            phase="1",
            status="running",
        )

    @app.get("/health")
    def health():
        return jsonify(status="healthy"), 200

    @app.get("/api/health")
    def api_health():
        return jsonify(status="healthy"), 200

    return app
