from datetime import date, datetime, time

from app.core.availability import get_available_slots
from app.extensions import db
from app.models import (
    Appointment,
    Establishment,
    Schedule,
    ScheduleException,
    Service,
)


def test_returns_available_slots(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )
        db.session.add(establishment)
        db.session.commit()

        service = Service(
            establishment_id=establishment.id,
            name="Serviço Teste",
            description="Serviço utilizado no teste",
            duration_minutes=30,
            price=50.00,
            active=True,
        )
        db.session.add(service)
        db.session.commit()

        schedule = Schedule(
            establishment_id=establishment.id,
            weekday=0,
            opening_time=time(8, 0),
            closing_time=time(10, 0),
            active=True,
        )
        db.session.add(schedule)
        db.session.commit()

        slots = get_available_slots(
            establishment_id=establishment.id,
            service_id=service.id,
            target_date=date(2026, 9, 28),
        )

        assert len(slots) == 4
        assert slots[0].time() == time(8, 0)
        assert slots[1].time() == time(8, 30)
        assert slots[2].time() == time(9, 0)
        assert slots[3].time() == time(9, 30)


def test_does_not_return_occupied_slot(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )
        db.session.add(establishment)
        db.session.commit()

        service = Service(
            establishment_id=establishment.id,
            name="Serviço Teste",
            description="Serviço utilizado no teste",
            duration_minutes=30,
            price=50.00,
            active=True,
        )
        db.session.add(service)
        db.session.commit()

        schedule = Schedule(
            establishment_id=establishment.id,
            weekday=0,
            opening_time=time(8, 0),
            closing_time=time(10, 0),
            active=True,
        )
        db.session.add(schedule)
        db.session.commit()

        appointment = Appointment(
            establishment_id=establishment.id,
            service_id=service.id,
            customer_name="Cliente Teste",
            customer_phone="11988888888",
            starts_at=datetime(2026, 9, 28, 9, 0),
            ends_at=datetime(2026, 9, 28, 9, 30),
            status="scheduled",
        )
        db.session.add(appointment)
        db.session.commit()

        slots = get_available_slots(
            establishment_id=establishment.id,
            service_id=service.id,
            target_date=date(2026, 9, 28),
        )

        available_times = [slot.time() for slot in slots]

        assert time(8, 0) in available_times
        assert time(8, 30) in available_times
        assert time(9, 0) not in available_times
        assert time(9, 30) in available_times


def test_schedule_exception_changes_opening_hours(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )
        db.session.add(establishment)
        db.session.commit()

        service = Service(
            establishment_id=establishment.id,
            name="Serviço Teste",
            description="Serviço utilizado no teste",
            duration_minutes=30,
            price=50.00,
            active=True,
        )
        db.session.add(service)
        db.session.commit()

        schedule = Schedule(
            establishment_id=establishment.id,
            weekday=0,
            opening_time=time(8, 0),
            closing_time=time(10, 0),
            active=True,
        )
        db.session.add(schedule)
        db.session.commit()

        exception = ScheduleException(
            establishment_id=establishment.id,
            date=date(2026, 9, 28),
            opening_time=time(9, 0),
            closing_time=time(11, 0),
            closed=False,
        )
        db.session.add(exception)
        db.session.commit()

        slots = get_available_slots(
            establishment_id=establishment.id,
            service_id=service.id,
            target_date=date(2026, 9, 28),
        )

        available_times = [slot.time() for slot in slots]

        assert time(8, 0) not in available_times
        assert time(8, 30) not in available_times
        assert time(9, 0) in available_times
        assert time(9, 30) in available_times
        assert time(10, 0) in available_times
        assert time(10, 30) in available_times


def test_schedule_exception_closes_establishment(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )
        db.session.add(establishment)
        db.session.commit()

        service = Service(
            establishment_id=establishment.id,
            name="Serviço Teste",
            description="Serviço utilizado no teste",
            duration_minutes=30,
            price=50.00,
            active=True,
        )
        db.session.add(service)
        db.session.commit()

        schedule = Schedule(
            establishment_id=establishment.id,
            weekday=0,
            opening_time=time(8, 0),
            closing_time=time(18, 0),
            active=True,
        )
        db.session.add(schedule)
        db.session.commit()

        exception = ScheduleException(
            establishment_id=establishment.id,
            date=date(2026, 9, 28),
            opening_time=None,
            closing_time=None,
            closed=True,
        )
        db.session.add(exception)
        db.session.commit()

        slots = get_available_slots(
            establishment_id=establishment.id,
            service_id=service.id,
            target_date=date(2026, 9, 28),
        )

        assert slots == []


def test_schedule_exception_changes_closing_time(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )
        db.session.add(establishment)
        db.session.commit()

        service = Service(
            establishment_id=establishment.id,
            name="Serviço Teste",
            description="Serviço utilizado no teste",
            duration_minutes=30,
            price=50.00,
            active=True,
        )
        db.session.add(service)
        db.session.commit()

        schedule = Schedule(
            establishment_id=establishment.id,
            weekday=0,
            opening_time=time(8, 0),
            closing_time=time(18, 0),
            active=True,
        )
        db.session.add(schedule)
        db.session.commit()

        exception = ScheduleException(
            establishment_id=establishment.id,
            date=date(2026, 9, 28),
            opening_time=time(8, 0),
            closing_time=time(14, 0),
            closed=False,
        )
        db.session.add(exception)
        db.session.commit()

        slots = get_available_slots(
            establishment_id=establishment.id,
            service_id=service.id,
            target_date=date(2026, 9, 28),
        )

        available_times = [slot.time() for slot in slots]

        assert time(8, 0) in available_times
        assert time(13, 30) in available_times
        assert time(14, 0) not in available_times
        assert time(14, 30) not in available_times
        assert time(17, 30) not in available_times


def test_schedule_exception_changes_opening_time(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )
        db.session.add(establishment)
        db.session.commit()

        service = Service(
            establishment_id=establishment.id,
            name="Serviço Teste",
            description="Serviço utilizado no teste",
            duration_minutes=30,
            price=50.00,
            active=True,
        )
        db.session.add(service)
        db.session.commit()

        schedule = Schedule(
            establishment_id=establishment.id,
            weekday=0,
            opening_time=time(8, 0),
            closing_time=time(18, 0),
            active=True,
        )
        db.session.add(schedule)
        db.session.commit()

        exception = ScheduleException(
            establishment_id=establishment.id,
            date=date(2026, 9, 28),
            opening_time=time(10, 0),
            closing_time=time(18, 0),
            closed=False,
        )
        db.session.add(exception)
        db.session.commit()

        slots = get_available_slots(
            establishment_id=establishment.id,
            service_id=service.id,
            target_date=date(2026, 9, 28),
        )

        available_times = [slot.time() for slot in slots]

        assert time(8, 0) not in available_times
        assert time(8, 30) not in available_times
        assert time(9, 0) not in available_times
        assert time(9, 30) not in available_times
        assert time(10, 0) in available_times
        assert time(10, 30) in available_times
        assert time(17, 30) in available_times