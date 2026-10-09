from unittest.mock import patch

from werkzeug.exceptions import BadRequest

from app.core.errors import APIError


def test_internal_error_returns_generic_response_and_logs_exception(
    app,
    client,
):
    app.config["PROPAGATE_EXCEPTIONS"] = False

    def raise_internal_error():
        raise RuntimeError("detalhe interno confidencial")

    app.add_url_rule(
        "/_test/internal-error",
        endpoint="test_internal_error",
        view_func=raise_internal_error,
    )

    with patch.object(app.logger, "error", wraps=app.logger.error) as log_error:
        response = client.get("/_test/internal-error")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error"}
    assert "detalhe interno confidencial" not in response.get_data(as_text=True)
    log_error.assert_called_once()


def test_api_error_preserves_status_and_details(app, client):
    def raise_api_error():
        raise APIError(
            "Dados inválidos",
            status_code=422,
            details={"field": "email"},
        )

    app.add_url_rule(
        "/_test/api-error",
        endpoint="test_api_error",
        view_func=raise_api_error,
    )

    response = client.get("/_test/api-error")

    assert response.status_code == 422
    assert response.get_json() == {
        "error": "Dados inválidos",
        "details": {"field": "email"},
    }


def test_bad_request_returns_generic_response(app, client):
    def raise_bad_request():
        raise BadRequest()

    app.add_url_rule(
        "/_test/bad-request",
        endpoint="test_bad_request",
        view_func=raise_bad_request,
    )

    response = client.get("/_test/bad-request")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Bad request"}


def test_method_not_allowed_returns_generic_response(client):
    response = client.post("/health")

    assert response.status_code == 405
    assert response.get_json() == {"error": "Method not allowed"}
