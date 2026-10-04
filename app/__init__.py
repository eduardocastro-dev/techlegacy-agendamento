from flask import Flask, jsonify

from .config import Config
from .extensions import db, migrate
from .core.errors import APIError
from .services.routes import services_bp
from .schedules.routes import schedules_bp
from .schedule_exceptions.routes import (schedule_exceptions_bp,)
from .appointments.routes import appointments_bp



def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(services_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(schedule_exceptions_bp)
    app.register_blueprint(appointments_bp)

    from .models import Establishment

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            "error": error.message
        }

        if error.details:
            response["details"] = error.details

        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        return jsonify({
            "error": "Bad request"
        }), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            "error": "Resource not found"
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            "error": "Method not allowed"
        }), 405

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "message": "TechLegacy Agendamento API is running"
        }

    return app