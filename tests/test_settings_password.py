def test_update_password_success(
    client,
    auth_headers,
):

    response = client.put(
        "/settings/password",
        headers=auth_headers,
        json={
            "current_password": "123456",
            "new_password": "nova123",
            "confirm_password": "nova123",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Password updated successfully"


def test_update_password_wrong_current_password(
    client,
    auth_headers,
):

    response = client.put(
        "/settings/password",
        headers=auth_headers,
        json={
            "current_password": "senhaerrada",
            "new_password": "nova123",
            "confirm_password": "nova123",
        },
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Current password is incorrect"


def test_update_password_confirmation_mismatch(
    client,
    auth_headers,
):

    response = client.put(
        "/settings/password",
        headers=auth_headers,
        json={
            "current_password": "123456",
            "new_password": "nova123",
            "confirm_password": "outra123",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert "confirm_password" in data["details"]


def test_update_password_invalid_new_password(
    client,
    auth_headers,
):

    response = client.put(
        "/settings/password",
        headers=auth_headers,
        json={
            "current_password": "123456",
            "new_password": "123",
            "confirm_password": "123",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert "new_password" in data["details"]
