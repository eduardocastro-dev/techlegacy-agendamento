from datetime import date

from app.extensions import db
from app.models import Appointment, Establishment, Service


def create_establishment():
    establishment = Establishment(
        name="TechLegacy Test",
        slug="techlegacy-test",
    )

    db.session.add(establishment)
    db.session.commit()

    return establishment


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


def create_schedule(client, establishment_id):
    response = client.post(
        "/schedules",
        json={
            "establishment_id": establishment_id,
            "weekday": date(2026, 10, 5).weekday(),
            "opening_time": "08:00",
            "closing_time": "18:00",
        },
    )

    assert response.status_code == 201


def test_create_appointment(client):
    establishment = create_establishment()
    service = create_service(establishment.id)

    create_schedule(
        client,
        establishment.id,
    )

    response = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["establishment_id"] == establishment.id
    assert data["service_id"] == service.id
    assert data["customer_name"] == "João"
    assert data["starts_at"] == "2026-10-05T09:00:00"
    assert data["ends_at"] == "2026-10-05T09:30:00"
    assert data["status"] == "scheduled"


def test_create_appointment_occupied_slot(client):
    establishment = create_establishment()
    service = create_service(establishment.id)

    create_schedule(
        client,
        establishment.id,
    )

    first = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert first.status_code == 201

    second = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "Maria",
            "customer_phone": "11888888888",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert second.status_code == 409

    data = second.get_json()

    assert (
        data["error"]
        == "Selected time slot is not available"
    )


def test_create_appointment_outside_schedule(client):
    establishment = create_establishment()
    service = create_service(establishment.id)

    create_schedule(
        client,
        establishment.id,
    )

    response = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T18:00:00",
        },
    )

    assert response.status_code == 409


def test_list_appointments(client):
    establishment = create_establishment()
    service = create_service(establishment.id)

    create_schedule(
        client,
        establishment.id,
    )

    client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    response = client.get(
        f"/appointments?establishment_id="
        f"{establishment.id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["customer_name"] == "João"


def test_get_appointment(client):
    establishment = create_establishment()
    service = create_service(establishment.id)

    create_schedule(
        client,
        establishment.id,
    )

    create_response = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    appointment_id = (
        create_response.get_json()["id"]
    )

    response = client.get(
        f"/appointments/{appointment_id}"
        f"?establishment_id={establishment.id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == appointment_id


def test_cancel_appointment_releases_slot(client):
    establishment = create_establishment()
    service = create_service(establishment.id)

    create_schedule(
        client,
        establishment.id,
    )

    create_response = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "João",
            "customer_phone": "11999999999",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    appointment_id = (
        create_response.get_json()["id"]
    )

    response = client.delete(
        f"/appointments/{appointment_id}"
        f"?establishment_id={establishment.id}"
    )

    assert response.status_code == 200

    appointment = db.session.get(
        Appointment,
        appointment_id,
    )

    assert appointment.status == "cancelled"

    new_response = client.post(
        "/appointments",
        json={
            "establishment_id": establishment.id,
            "service_id": service.id,
            "customer_name": "Maria",
            "customer_phone": "11888888888",
            "starts_at": "2026-10-05T09:00:00",
        },
    )

    assert new_response.status_code == 201