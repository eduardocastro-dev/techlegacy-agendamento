from datetime import date, datetime, time

from app.extensions import db
from app.models import (
    Appointment,
    Schedule,
    ScheduleException,
    Service,
)


def create_service(establishment_id):
    service = Service(
        establishment_id=establishment_id,
        name="Corte de cabelo",
        description="Corte masculino",
        duration_minutes=30,
        price=50.00,
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    return service.id


def create_schedule(establishment_id, weekday):
    schedule = Schedule(
        establishment_id=establishment_id,
        weekday=weekday,
        opening_time=time(9, 0),
        closing_time=time(18, 0),
        active=True,
    )

    db.session.add(schedule)
    db.session.commit()

    return schedule.id


def create_appointment(
    establishment_id,
    service_id,
    starts_at,
    ends_at,
    status="scheduled",
):
    appointment = Appointment(
        establishment_id=establishment_id,
        service_id=service_id,
        customer_name="Cliente Teste",
        customer_phone="11999999999",
        starts_at=starts_at,
        ends_at=ends_at,
        status=status,
    )

    db.session.add(appointment)
    db.session.commit()

    return appointment.id


def test_get_agenda_requires_authentication(client):
    response = client.get("/dashboard/agenda?date=2026-09-28")

    assert response.status_code == 401


def test_get_agenda_requires_date(client, auth_headers):
    response = client.get(
        "/dashboard/agenda",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Query parameter 'date' is required"}


def test_get_agenda_validates_date_format(client, auth_headers):
    response = client.get(
        "/dashboard/agenda?date=28-09-2026",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid date format. Use YYYY-MM-DD"}


def test_get_agenda_returns_regular_schedule(
    client,
    auth_headers,
    establishment,
):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        target_date.weekday(),
    )

    response = client.get(
        "/dashboard/agenda?date=2026-09-28",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["date"] == "2026-09-28"
    assert data["weekday"] == 0

    assert data["schedule"] == {
        "opening_time": "09:00",
        "closing_time": "18:00",
        "closed": False,
    }

    assert data["appointments"] == []


def test_get_agenda_returns_closed_exception(
    client,
    auth_headers,
    establishment,
):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        target_date.weekday(),
    )

    exception = ScheduleException(
        establishment_id=establishment,
        date=target_date,
        opening_time=None,
        closing_time=None,
        closed=True,
    )

    db.session.add(exception)
    db.session.commit()

    response = client.get(
        "/dashboard/agenda?date=2026-09-28",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["schedule"] == {
        "opening_time": None,
        "closing_time": None,
        "closed": True,
    }


def test_get_agenda_returns_exception_schedule(
    client,
    auth_headers,
    establishment,
):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        target_date.weekday(),
    )

    exception = ScheduleException(
        establishment_id=establishment,
        date=target_date,
        opening_time=time(10, 0),
        closing_time=time(16, 0),
        closed=False,
    )

    db.session.add(exception)
    db.session.commit()

    response = client.get(
        "/dashboard/agenda?date=2026-09-28",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["schedule"] == {
        "opening_time": "10:00",
        "closing_time": "16:00",
        "closed": False,
    }


def test_get_agenda_returns_appointments(
    client,
    auth_headers,
    establishment,
):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        target_date.weekday(),
    )

    service_id = create_service(establishment)

    create_appointment(
        establishment,
        service_id,
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 10, 30),
    )

    response = client.get(
        "/dashboard/agenda?date=2026-09-28",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["appointments"]) == 1

    appointment = data["appointments"][0]

    assert appointment["service_id"] == service_id
    assert appointment["service_name"] == "Corte de cabelo"
    assert appointment["customer_name"] == "Cliente Teste"
    assert appointment["customer_phone"] == "11999999999"
    assert appointment["starts_at"] == "2026-09-28T10:00:00"
    assert appointment["ends_at"] == "2026-09-28T10:30:00"
    assert appointment["status"] == "scheduled"


def test_get_agenda_does_not_return_other_establishment_appointments(
    client,
    auth_headers,
    establishment,
):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        target_date.weekday(),
    )

    service_id = create_service(establishment)

    create_appointment(
        establishment,
        service_id,
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 10, 30),
    )

    response = client.get(
        "/dashboard/agenda?date=2026-09-28",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["appointments"]) == 1
    assert data["appointments"][0]["customer_name"] == "Cliente Teste"
