from datetime import date, datetime, time

from app.extensions import db
from app.models import (
    Appointment,
    Schedule,
    ScheduleException,
    Service,
    Establishment,
)
from app.dashboard.agenda_service import get_agenda_data


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


def create_schedule(establishment_id, weekday=0):
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


def test_agenda_returns_regular_schedule(establishment):
    target_date = date(2026, 9, 28)  # segunda-feira

    create_schedule(
        establishment,
        weekday=target_date.weekday(),
    )

    result = get_agenda_data(
        establishment,
        target_date,
    )

    assert result["date"] == target_date
    assert result["weekday"] == 0
    assert result["schedule"]["closed"] is False
    assert result["schedule"]["opening_time"] == time(9, 0)
    assert result["schedule"]["closing_time"] == time(18, 0)


def test_agenda_closed_when_there_is_no_schedule(establishment):
    target_date = date(2026, 9, 28)

    result = get_agenda_data(
        establishment,
        target_date,
    )

    assert result["schedule"]["closed"] is True
    assert result["schedule"]["opening_time"] is None
    assert result["schedule"]["closing_time"] is None


def test_agenda_closed_by_exception(establishment):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        weekday=target_date.weekday(),
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

    result = get_agenda_data(
        establishment,
        target_date,
    )

    assert result["schedule"]["closed"] is True
    assert result["schedule"]["opening_time"] is None
    assert result["schedule"]["closing_time"] is None


def test_agenda_exception_changes_schedule(establishment):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        weekday=target_date.weekday(),
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

    result = get_agenda_data(
        establishment,
        target_date,
    )

    assert result["schedule"]["closed"] is False
    assert result["schedule"]["opening_time"] == time(10, 0)
    assert result["schedule"]["closing_time"] == time(16, 0)


def test_agenda_returns_appointments_in_order(establishment):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        weekday=target_date.weekday(),
    )

    service_id = create_service(establishment)

    first_id = create_appointment(
        establishment,
        service_id,
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 10, 30),
    )

    second_id = create_appointment(
        establishment,
        service_id,
        datetime(2026, 9, 28, 14, 0),
        datetime(2026, 9, 28, 14, 30),
    )

    result = get_agenda_data(
        establishment,
        target_date,
    )

    appointments = result["appointments"]

    assert len(appointments) == 2
    assert appointments[0].id == first_id
    assert appointments[1].id == second_id


def test_agenda_does_not_return_appointments_from_another_establishment(
    establishment,
):
    target_date = date(2026, 9, 28)

    create_schedule(
        establishment,
        weekday=target_date.weekday(),
    )

    service_id = create_service(establishment)

    create_appointment(
        establishment,
        service_id,
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 10, 30),
    )

    other_establishment = Establishment(
        name="Outro Estabelecimento",
        slug="outro-estabelecimento",
        phone="11988888888",
    )

    db.session.add(other_establishment)
    db.session.commit()

    other_service = create_service(other_establishment.id)

    other_appointment_id = create_appointment(
        other_establishment.id,
        other_service,
        datetime(2026, 9, 28, 11, 0),
        datetime(2026, 9, 28, 11, 30),
    )

    result = get_agenda_data(
        establishment,
        target_date,
    )

    appointment_ids = [appointment.id for appointment in result["appointments"]]

    assert other_appointment_id not in appointment_ids
