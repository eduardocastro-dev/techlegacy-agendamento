def test_create_service(client, auth_headers, establishment):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["establishment_id"] == establishment
    assert data["name"] == "Corte de cabelo"
    assert data["description"] == "Corte masculino"
    assert data["duration_minutes"] == 30
    assert data["price"] == 50.00
    assert data["active"] is True


def test_list_services(client, auth_headers, establishment):
    client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Barba",
            "description": "Barba completa",
            "duration_minutes": 20,
            "price": 30.00,
        },
    )

    response = client.get(
        "/services",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    assert data[0]["name"] == "Corte de cabelo"
    assert data[0]["duration_minutes"] == 30
    assert data[0]["price"] == 50.00

    assert data[1]["name"] == "Barba"
    assert data[1]["duration_minutes"] == 20
    assert data[1]["price"] == 30.00


def test_get_service(client, auth_headers, establishment):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.get(
        f"/services/{service_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == service_id
    assert data["establishment_id"] == establishment
    assert data["name"] == "Corte de cabelo"
    assert data["description"] == "Corte masculino"
    assert data["duration_minutes"] == 30
    assert data["price"] == 50.00
    assert data["active"] is True


def test_get_service_not_found(client, auth_headers):
    response = client.get(
        "/services/999",
        headers=auth_headers,
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Service not found"


def test_update_service(client, auth_headers, establishment):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.put(
        f"/services/{service_id}",
        headers=auth_headers,
        json={
            "name": "Corte masculino",
            "description": "Corte masculino completo",
            "duration_minutes": 40,
            "price": 60.00,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == service_id
    assert data["establishment_id"] == establishment
    assert data["name"] == "Corte masculino"
    assert data["description"] == "Corte masculino completo"
    assert data["duration_minutes"] == 40
    assert data["price"] == 60.00
    assert data["active"] is True


def test_update_service_partial(client, auth_headers):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Barba",
            "description": "Barba completa",
            "duration_minutes": 20,
            "price": 30.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.put(
        f"/services/{service_id}",
        headers=auth_headers,
        json={
            "price": 35.00,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "Barba"
    assert data["description"] == "Barba completa"
    assert data["duration_minutes"] == 20
    assert data["price"] == 35.00


def test_update_service_not_found(client, auth_headers):
    response = client.put(
        "/services/999",
        headers=auth_headers,
        json={
            "name": "Serviço inexistente",
        },
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Service not found"


def test_delete_service(client, auth_headers):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.delete(
        f"/services/{service_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Service deactivated successfully"


def test_deleted_service_is_not_listed(
    client,
    auth_headers,
):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Barba",
            "description": "Barba completa",
            "duration_minutes": 20,
            "price": 30.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.delete(
        f"/services/{service_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    response = client.get(
        "/services",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data == []


def test_delete_service_not_found(
    client,
    auth_headers,
):
    response = client.delete(
        "/services/999",
        headers=auth_headers,
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Service not found"


def test_create_service_without_required_fields(
    client,
    auth_headers,
):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert "duration_minutes" in data["details"]
    assert "price" in data["details"]


def test_create_service_with_invalid_duration(
    client,
    auth_headers,
):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte",
            "duration_minutes": 0,
            "price": 50,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert data["details"]["duration_minutes"] == "Must be greater than zero"


def test_create_service_with_negative_price(
    client,
    auth_headers,
):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte",
            "duration_minutes": 30,
            "price": -10,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert data["details"]["price"] == "Must be greater than or equal to zero"


def test_list_services_without_auth(client):
    response = client.get("/services")

    assert response.status_code == 401


def test_get_service_without_auth(client):
    response = client.get("/services/1")

    assert response.status_code == 401


def test_update_service_with_invalid_data(
    client,
    auth_headers,
):
    create_response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert create_response.status_code == 201

    service_id = create_response.get_json()["id"]

    response = client.put(
        f"/services/{service_id}",
        headers=auth_headers,
        json={
            "duration_minutes": 0,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert data["details"]["duration_minutes"] == "Must be greater than zero"


def test_service_isolation_between_establishments(
    client,
    app,
    auth_headers,
):
    from app.extensions import db
    from app.models import Establishment, User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        establishment_2 = Establishment(
            name="Outro Estabelecimento",
            slug="outro-estabelecimento",
            phone="11888888888",
        )

        db.session.add(establishment_2)
        db.session.commit()

        user_2 = User(
            establishment_id=establishment_2.id,
            email="outro@exemplo.com",
            password_hash=generate_password_hash("123456"),
        )

        db.session.add(user_2)
        db.session.commit()

    response = client.post(
        "/services",
        headers=auth_headers,
        json={
            "name": "Serviço privado",
            "description": "Serviço do estabelecimento 1",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.post(
        "/auth/login",
        json={
            "email": "outro@exemplo.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    token = response.get_json()["access_token"]

    auth_headers_2 = {"Authorization": f"Bearer {token}"}

    response = client.get(
        f"/services/{service_id}",
        headers=auth_headers_2,
    )

    assert response.status_code == 404

    response = client.put(
        f"/services/{service_id}",
        headers=auth_headers_2,
        json={
            "name": "Tentativa de alteração",
        },
    )

    assert response.status_code == 404

    response = client.delete(
        f"/services/{service_id}",
        headers=auth_headers_2,
    )

    assert response.status_code == 404
