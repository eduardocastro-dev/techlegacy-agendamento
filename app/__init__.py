from flask import Flask

from .config import Config
from .extensions import db, migrate
from .services.routes import services_bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(services_bp)

    from .models import Establishment

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "message": "TechLegacy Agendamento API is running"
        }

    return app