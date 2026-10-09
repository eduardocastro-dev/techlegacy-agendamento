def create_service(client, auth_headers, name="Corte"):
    response = client.post(
        "/services",
        headers=auth_headers,
        json={"name": name, "duration_minutes": 30, "price": 50},
    )
    assert response.status_code == 201
    return response.get_json()


def test_create_professional(client, auth_headers, establishment):
    service = create_service(client, auth_headers)
    response = client.post(
        "/professionals",
        headers=auth_headers,
        json={"name": "Ana Souza", "service_ids": [service["id"]]},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["establishment_id"] == establishment
    assert data["name"] == "Ana Souza"
    assert data["active"] is True
    assert data["service_ids"] == [service["id"]]
    assert data["services"] == ["Corte"]


def test_list_professionals_can_include_inactive(client, auth_headers):
    created = client.post(
        "/professionals", headers=auth_headers, json={"name": "Ana"}
    ).get_json()
    client.delete(f"/professionals/{created['id']}", headers=auth_headers)

    active_response = client.get("/professionals", headers=auth_headers)
    all_response = client.get(
        "/professionals?include_inactive=true", headers=auth_headers
    )
    assert active_response.status_code == 200
    assert active_response.get_json() == []
    assert len(all_response.get_json()) == 1
    assert all_response.get_json()[0]["active"] is False


def test_update_professional_name_and_services(client, auth_headers):
    service = create_service(client, auth_headers)
    created = client.post(
        "/professionals", headers=auth_headers, json={"name": "Ana"}
    ).get_json()
    response = client.put(
        f"/professionals/{created['id']}",
        headers=auth_headers,
        json={"name": "Ana Souza", "service_ids": [service["id"]]},
    )
    assert response.status_code == 200
    assert response.get_json()["name"] == "Ana Souza"
    assert response.get_json()["service_ids"] == [service["id"]]


def test_professional_cannot_be_assigned_service_from_another_establishment(
    client, auth_headers, app
):
    from app.extensions import db
    from app.models import Establishment, Service

    with app.app_context():
        other = Establishment(name="Outro", slug="outro-estabelecimento")
        db.session.add(other)
        db.session.flush()
        service = Service(
            establishment_id=other.id,
            name="Serviço de outro estabelecimento",
            duration_minutes=30,
            price=50,
            active=True,
        )
        db.session.add(service)
        db.session.commit()
        other_service_id = service.id

    response = client.post(
        "/professionals",
        headers=auth_headers,
        json={"name": "Ana", "service_ids": [other_service_id]},
    )
    assert response.status_code == 400


def test_create_professional_requires_name(client, auth_headers):
    response = client.post("/professionals", headers=auth_headers, json={})
    assert response.status_code == 400
    assert response.get_json()["details"]["name"] == "This field is required"
