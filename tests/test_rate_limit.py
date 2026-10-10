from flask import Flask, jsonify

from app.extensions import limiter


def create_rate_limit_test_app():
    """Cria uma aplicação isolada para testar os limites."""

    app = Flask(__name__)

    app.config.update(
        TESTING=True,
        RATELIMIT_ENABLED=True,
        RATELIMIT_STORAGE_URI="memory://",
    )

    limiter.init_app(app)

    @app.post("/test-login")
    @limiter.limit("5 per minute")
    def test_login():
        return jsonify({"message": "ok"}), 200

    @app.post("/test-register")
    @limiter.limit("3 per hour")
    def test_register():
        return jsonify({"message": "ok"}), 200

    return app


def test_login_rate_limit():
    app = create_rate_limit_test_app()
    client = app.test_client()

    for _ in range(5):
        response = client.post("/test-login")
        assert response.status_code == 200

    response = client.post("/test-login")

    assert response.status_code == 429


def test_register_rate_limit():
    app = create_rate_limit_test_app()
    client = app.test_client()

    for _ in range(3):
        response = client.post("/test-register")
        assert response.status_code == 200

    response = client.post("/test-register")

    assert response.status_code == 429
