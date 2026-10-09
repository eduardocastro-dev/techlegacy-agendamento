from datetime import date, datetime, timedelta, timezone

from app.models import Appointment, Schedule, ScheduleException, Service


def to_naive(dt: datetime) -> datetime:
    """Converte para UTC e remove tzinfo. Se já for naive, devolve igual."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def get_available_slots(
    establishment_id: int,
    service_id: int,
    target_date: date,
    exclude_appointment_id: int | None = None,
):
    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        return []

    service_duration_minutes = service.duration_minutes

    weekday = target_date.weekday()

    schedule = Schedule.query.filter_by(
        establishment_id=establishment_id,
        weekday=weekday,
        active=True,
    ).first()

    if not schedule:
        return []

    exception = ScheduleException.query.filter_by(
        establishment_id=establishment_id,
        date=target_date,
    ).first()

    if exception and exception.closed:
        return []

    opening_time = schedule.opening_time
    closing_time = schedule.closing_time

    if exception:
        if exception.opening_time is not None:
            opening_time = exception.opening_time

        if exception.closing_time is not None:
            closing_time = exception.closing_time

    start_datetime = datetime.combine(
        target_date,
        opening_time,
    )

    end_datetime = datetime.combine(
        target_date,
        closing_time,
    )

    appointments_query = Appointment.query.filter(
        Appointment.establishment_id == establishment_id,
        Appointment.starts_at < end_datetime,
        Appointment.ends_at > start_datetime,
        Appointment.status != "cancelled",
    )

    if exclude_appointment_id is not None:
        appointments_query = appointments_query.filter(
            Appointment.id != exclude_appointment_id
        )

    appointments = appointments_query.all()

    # Normaliza os horários dos agendamentos antes de comparar
    busy_ranges = [(to_naive(a.starts_at), to_naive(a.ends_at)) for a in appointments]

    slots = []

    current = start_datetime
    duration = timedelta(minutes=service_duration_minutes)

    while current + duration <= end_datetime:
        slot_end = current + duration

        has_conflict = any(
            busy_start < slot_end and busy_end > current
            for busy_start, busy_end in busy_ranges
        )

        if not has_conflict:
            slots.append(current)

        current += duration

    return slots
