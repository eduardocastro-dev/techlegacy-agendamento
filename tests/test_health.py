from app import create_app


def test_health():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-" + ("a" * 32),
            "JWT_SECRET_KEY": "test-jwt-secret-" + ("b" * 32),
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
