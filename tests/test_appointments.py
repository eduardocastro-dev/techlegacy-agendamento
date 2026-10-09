from datetime import date

from app.extensions import db
from app.models import Appointment, Establishment, Professional, Service


def create_service(establishment_id):
    service = Service(
        establishment_id=establishment_id,
        name="Corte",
        duration_minutes=30,
        price=50,
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    return service


def create_professional(establishment_id, service, name):
    professional = Professional(
        establishment_id=establishment_id,
        name=name,
        active=True,
    )
    professional.services.append(service)

    db.session.add(professional)
    db.session.commit()

    return professional


def create_schedule(client, auth_headers):
    response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "weekday": date(2026, 10, 5).weekday(),
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 201


def create_appointment(
    client,
    auth_headers,
    service_id,
    starts_at="2026-10-05T09:00:00",
    customer_name="João",
    customer_phone="11999999999",
    professional_id=None,
):
    payload = {
        "service_id": service_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "starts_at": starts_at,
    }

    if professional_id is not None:
        payload["professional_id"] = professional_id

    return client.post(
        "/appointments",
        headers=auth_headers,
        json=payload,
    )


def test_create_appointment(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["establishment_id"] == establishment
    assert data["service_id"] == service.id
    assert data["customer_name"] == "João"
    assert data["starts_at"] == "2026-10-05T09:00:00"
    assert data["ends_at"] == "2026-10-05T09:30:00"
    assert data["status"] == "scheduled"


def test_create_appointment_occupied_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    first = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert first.status_code == 201

    second = create_appointment(
        client,
        auth_headers,
        service.id,
        customer_name="Maria",
        customer_phone="11888888888",
    )

    assert second.status_code == 409

    data = second.get_json()

    assert data["error"] == "Selected time slot is not available"


def test_create_appointment_outside_schedule(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    response = create_appointment(
        client,
        auth_headers,
        service.id,
        starts_at="2026-10-05T18:00:00",
    )

    assert response.status_code == 409


def test_list_appointments(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_appointment(
        client,
        auth_headers,
        service.id,
    )

    response = client.get(
        "/appointments",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["customer_name"] == "João"


def test_get_appointment(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    response = client.get(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == appointment_id


def test_cancel_appointment_releases_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    response = client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    appointment = db.session.get(
        Appointment,
        appointment_id,
    )

    assert appointment.status == "cancelled"

    new_response = create_appointment(
        client,
        auth_headers,
        service.id,
        customer_name="Maria",
        customer_phone="11888888888",
    )

    assert new_response.status_code == 201


def test_update_appointment_same_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == appointment_id
    assert data["starts_at"] == "2026-10-05T09:00:00"
    assert data["ends_at"] == "2026-10-05T09:30:00"


def test_update_appointment_to_available_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={
            "starts_at": "2026-10-05T10:00:00",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["starts_at"] == "2026-10-05T10:00:00"
    assert data["ends_at"] == "2026-10-05T10:30:00"


def test_update_appointment_to_occupied_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    first = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert first.status_code == 201

    second = create_appointment(
        client,
        auth_headers,
        service.id,
        starts_at="2026-10-05T10:00:00",
        customer_name="Maria",
        customer_phone="11888888888",
    )

    assert second.status_code == 201

    second_id = second.get_json()["id"]

    response = client.put(
        f"/appointments/{second_id}",
        headers=auth_headers,
        json={
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Selected time slot is not available"


def test_cancelled_appointment_can_be_reactivated_when_slot_is_available(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    cancel_response = client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
    )

    assert cancel_response.status_code == 200

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={
            "status": "scheduled",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "scheduled"


def test_cancelled_appointment_cannot_be_reactivated_on_occupied_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    first = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert first.status_code == 201

    second = create_appointment(
        client,
        auth_headers,
        service.id,
        starts_at="2026-10-05T10:00:00",
        customer_name="Maria",
        customer_phone="11888888888",
    )

    assert second.status_code == 201

    second_id = second.get_json()["id"]

    cancel_response = client.delete(
        f"/appointments/{second_id}",
        headers=auth_headers,
    )

    assert cancel_response.status_code == 200

    response = client.put(
        f"/appointments/{second_id}",
        headers=auth_headers,
        json={
            "starts_at": "2026-10-05T09:00:00",
            "status": "scheduled",
        },
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Selected time slot is not available"


def test_update_appointment_customer_data(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={
            "customer_name": "Maria",
            "customer_phone": "11888888888",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["customer_name"] == "Maria"
    assert data["customer_phone"] == "11888888888"


def test_update_appointment_invalid_status(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation error"
    assert data["details"]["status"] == "Must be scheduled or cancelled"


def test_appointment_isolation_between_establishments(
    client,
    auth_headers,
    establishment,
    app,
):
    service = create_service(establishment)

    create_schedule(
        client,
        auth_headers,
    )

    create_response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert create_response.status_code == 201

    appointment_id = create_response.get_json()["id"]

    with app.app_context():
        establishment_two = Establishment(
            name="Another Test",
            slug="another-test",
        )

        db.session.add(establishment_two)
        db.session.commit()

        from werkzeug.security import generate_password_hash

        from app.models import User

        user_two = User(
            establishment_id=establishment_two.id,
            email="another@test.com",
            password_hash=generate_password_hash("123456"),
        )

        db.session.add(user_two)
        db.session.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "another@test.com",
            "password": "123456",
        },
    )

    assert login_response.status_code == 200

    token_two = login_response.get_json()["access_token"]

    auth_headers_two = {"Authorization": f"Bearer {token_two}"}

    response = client.get(
        f"/appointments/{appointment_id}",
        headers=auth_headers_two,
    )

    assert response.status_code == 404

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers_two,
        json={
            "customer_name": "Tentativa",
        },
    )

    assert response.status_code == 404

    response = client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_headers_two,
    )

    assert response.status_code == 404


def test_create_appointment_without_auth(client):
    response = client.post(
        "/appointments",
        json={
            "service_id": 1,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert response.status_code == 401


def test_list_appointments_without_auth(client):
    response = client.get("/appointments")

    assert response.status_code == 401


def test_get_appointment_without_auth(client):
    response = client.get("/appointments/1")

    assert response.status_code == 401


def test_different_professionals_can_book_same_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)
    professional_one = create_professional(
        establishment,
        service,
        "Ana",
    )
    professional_two = create_professional(
        establishment,
        service,
        "Bruno",
    )

    create_schedule(client, auth_headers)

    first = create_appointment(
        client,
        auth_headers,
        service.id,
        professional_id=professional_one.id,
    )
    second = create_appointment(
        client,
        auth_headers,
        service.id,
        professional_id=professional_two.id,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json()["professional_id"] == professional_one.id
    assert second.get_json()["professional_id"] == professional_two.id


def test_same_professional_cannot_book_overlapping_slot(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)
    professional = create_professional(
        establishment,
        service,
        "Ana",
    )

    create_schedule(client, auth_headers)

    first = create_appointment(
        client,
        auth_headers,
        service.id,
        professional_id=professional.id,
    )
    second = create_appointment(
        client,
        auth_headers,
        service.id,
        customer_name="Maria",
        customer_phone="11888888888",
        professional_id=professional.id,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_appointment_without_preference_assigns_available_professional(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)
    professional_one = create_professional(
        establishment,
        service,
        "Ana",
    )
    professional_two = create_professional(
        establishment,
        service,
        "Bruno",
    )

    create_schedule(client, auth_headers)

    response = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert response.status_code == 201
    assert response.get_json()["professional_id"] in {
        professional_one.id,
        professional_two.id,
    }


def test_update_appointment_changes_professional(
    client,
    auth_headers,
    establishment,
):
    service = create_service(establishment)
    professional_one = create_professional(
        establishment,
        service,
        "Ana",
    )
    professional_two = create_professional(
        establishment,
        service,
        "Bruno",
    )

    create_schedule(client, auth_headers)

    created = create_appointment(
        client,
        auth_headers,
        service.id,
        professional_id=professional_one.id,
    )

    assert created.status_code == 201

    appointment_id = created.get_json()["id"]

    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={"professional_id": professional_two.id},
    )

    assert response.status_code == 200
    assert response.get_json()["professional_id"] == professional_two.id


def test_cannot_assign_professional_from_another_establishment(
    client,
    auth_headers,
    establishment,
):
    # Serviço e profissional do estabelecimento autenticado.
    service = create_service(establishment)
    create_schedule(client, auth_headers)

    created = create_appointment(
        client,
        auth_headers,
        service.id,
    )

    assert created.status_code == 201
    appointment_id = created.get_json()["id"]

    # Criamos um segundo estabelecimento.
    other_establishment = Establishment(
        name="Outro Estabelecimento",
        slug="outro-estabelecimento",
        phone="11888888888",
    )
    db.session.add(other_establishment)
    db.session.commit()

    # Profissional vinculado somente ao segundo estabelecimento.
    other_service = create_service(other_establishment.id)
    other_professional = create_professional(
        other_establishment.id,
        other_service,
        "Carlos",
    )

    # Tentamos atribuí-lo ao agendamento do primeiro estabelecimento.
    response = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={"professional_id": other_professional.id},
    )

    assert response.status_code == 400, response.get_json()
    assert response.get_json()["error"] == (
        "Professional is not available for this service"
    )
