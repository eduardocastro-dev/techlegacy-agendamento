from flask import Flask, jsonify

from app.config import Config


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "message": "TechLegacy Agendamento API is running",
            }
        )

    return app