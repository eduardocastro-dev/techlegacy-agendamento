from datetime import timedelta
from unittest.mock import patch

from flask_jwt_extended import create_access_token

from app.auth.context import get_current_user


def test_jwt_expiration_config(app):
    assert app.config["JWT_ACCESS_TOKEN_EXPIRES"] == timedelta(hours=2)


def test_jwt_location_config(app):
    assert app.config["JWT_TOKEN_LOCATION"] == ["headers"]


def test_request_size_limit(app):
    assert app.config["MAX_CONTENT_LENGTH"] == 1048576


def test_invalid_jwt_identity_returns_none(app):
    with app.app_context():
        with patch(
            "app.auth.context.get_jwt_identity",
            return_value="invalid-user-id",
        ):
            assert get_current_user() is None


def test_negative_jwt_identity_returns_none(app):
    with app.app_context():
        with patch(
            "app.auth.context.get_jwt_identity",
            return_value="-1",
        ):
            assert get_current_user() is None


def test_jwt_has_expiration_claim(app):
    from flask_jwt_extended import decode_token

    with app.app_context():
        token = create_access_token(identity="1")
        decoded = decode_token(token)

        assert "exp" in decoded
        assert decoded["exp"] > decoded["iat"]
