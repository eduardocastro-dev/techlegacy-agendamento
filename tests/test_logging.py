import logging

import pytest
from flask import abort

from app.core.logging_config import configure_logging


def test_configure_logging_default_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_debug_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    configure_logging()

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_invalid_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INVALID")

    with pytest.raises(ValueError, match="LOG_LEVEL inválido"):
        configure_logging()


def test_internal_server_error_response(app):
    @app.get("/test-internal-error")
    def test_internal_error():
        abort(500)

    client = app.test_client()

    response = client.get("/test-internal-error")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error"}
