def test_get_account(
    client,
    auth_headers,
    user,
    establishment,
):

    response = client.get(
        "/settings/account",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == user
    assert data["establishment_id"] == establishment
    assert data["email"] == "teste@exemplo.com"
    assert "password_hash" not in data


def test_update_account_email(
    client,
    auth_headers,
    user,
    establishment,
):

    response = client.put(
        "/settings/account",
        headers=auth_headers,
        json={
            "email": "novoemail@exemplo.com",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == user
    assert data["establishment_id"] == establishment
    assert data["email"] == "novoemail@exemplo.com"
    assert "password_hash" not in data


def test_update_account_duplicate_email(
    client,
    auth_headers,
    user,
    establishment,
):

    from app.extensions import db
    from app.models import User

    other_user = User(
        establishment_id=establishment,
        email="outro@exemplo.com",
        password_hash="fake-hash",
    )

    db.session.add(other_user)
    db.session.commit()

    response = client.put(
        "/settings/account",
        headers=auth_headers,
        json={
            "email": "outro@exemplo.com",
        },
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Email already registered"


def test_update_account_invalid_email(
    client,
    auth_headers,
):

    response = client.put(
        "/settings/account",
        headers=auth_headers,
        json={
            "email": "email-invalido",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert "email" in data["details"]
