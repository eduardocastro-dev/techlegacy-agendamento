from flask import Flask, jsonify

from app.auth.views import auth_views_bp
from app.core.logging_config import configure_logging
from app.public import public_bp

from .appointments.routes import appointments_bp
from .auth.routes import auth_bp
from .config import Config
from .core.errors import APIError
from .dashboard.routes import dashboard_bp
from .extensions import db, jwt, migrate
from .schedule_exceptions.routes import schedule_exceptions_bp
from .schedules.routes import schedules_bp
from .services.routes import services_bp
from .settings.routes import settings_bp


def validate_config(app):
    required_keys = (
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
    )

    missing_keys = [key for key in required_keys if not app.config.get(key)]

    if missing_keys:
        raise RuntimeError(
            "Configurações obrigatórias ausentes: " + ", ".join(missing_keys)
        )

    for key in ("SECRET_KEY", "JWT_SECRET_KEY"):
        value = app.config[key]

        if not isinstance(value, str) or len(value) < 32:
            raise RuntimeError(f"{key} deve conter pelo menos 32 caracteres.")


def create_app(test_config=None):
    configure_logging()

    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    validate_config(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_views_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(schedule_exceptions_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(public_bp)

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {"error": error.message}

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.get("/health")
    def health():
        return {"status": "ok", "message": "TechLegacy Agendamento API is running"}

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        if error.original_exception is None:
            app.logger.error("Erro interno HTTP 500.")

        return jsonify({"error": "Internal server error"}), 500

    return app
