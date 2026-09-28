from app.extensions import db
from app.models import Establishment


def test_create_service(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["establishment_id"] == establishment_id
    assert data["name"] == "Corte de cabelo"
    assert data["description"] == "Corte masculino"
    assert data["duration_minutes"] == 30
    assert data["price"] == 50.00
    assert data["active"] is True

def test_list_services(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Barba",
            "description": "Barba completa",
            "duration_minutes": 20,
            "price": 30.00,
        },
    )

    response = client.get(
        f"/services?establishment_id={establishment_id}"
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

def test_get_service(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.get(
        f"/services/{service_id}"
        f"?establishment_id={establishment_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == service_id
    assert data["establishment_id"] == establishment_id
    assert data["name"] == "Corte de cabelo"
    assert data["description"] == "Corte masculino"
    assert data["duration_minutes"] == 30
    assert data["price"] == 50.00
    assert data["active"] is True

def test_get_service_not_found(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.get(
        f"/services/999"
        f"?establishment_id={establishment_id}"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Service not found"

def test_update_service(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.put(
        f"/services/{service_id}"
        f"?establishment_id={establishment_id}",
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
    assert data["establishment_id"] == establishment_id
    assert data["name"] == "Corte masculino"
    assert data["description"] == "Corte masculino completo"
    assert data["duration_minutes"] == 40
    assert data["price"] == 60.00
    assert data["active"] is True

def test_update_service_partial(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Barba",
            "description": "Barba completa",
            "duration_minutes": 20,
            "price": 30.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.put(
        f"/services/{service_id}"
        f"?establishment_id={establishment_id}",
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

def test_update_service_not_found(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.put(
        f"/services/999"
        f"?establishment_id={establishment_id}",
        json={
            "name": "Serviço inexistente",
        },
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Service not found"

def test_delete_service(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Corte de cabelo",
            "description": "Corte masculino",
            "duration_minutes": 30,
            "price": 50.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.delete(
        f"/services/{service_id}"
        f"?establishment_id={establishment_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Service deactivated successfully"

def test_deleted_service_is_not_listed(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.post(
        "/services",
        json={
            "establishment_id": establishment_id,
            "name": "Barba",
            "description": "Barba completa",
            "duration_minutes": 20,
            "price": 30.00,
        },
    )

    assert response.status_code == 201

    service_id = response.get_json()["id"]

    response = client.delete(
        f"/services/{service_id}"
        f"?establishment_id={establishment_id}"
    )

    assert response.status_code == 200

    response = client.get(
        f"/services?establishment_id={establishment_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data == []

def test_delete_service_not_found(client, app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

    response = client.delete(
        f"/services/999"
        f"?establishment_id={establishment_id}"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Service not found"