from datetime import date, datetime, timedelta, timezone

from app.models import (
    Appointment,
    Professional,
    Schedule,
    ScheduleException,
    Service,
)


def to_naive(dt: datetime) -> datetime:
    """Converte para UTC e remove tzinfo. Se já for naive, devolve igual."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _get_schedule_window(establishment_id: int, target_date: date):
    weekday = target_date.weekday()

    schedule = Schedule.query.filter_by(
        establishment_id=establishment_id,
        weekday=weekday,
        active=True,
    ).first()

    if not schedule:
        return None

    exception = ScheduleException.query.filter_by(
        establishment_id=establishment_id,
        date=target_date,
    ).first()

    if exception and exception.closed:
        return None

    opening_time = schedule.opening_time
    closing_time = schedule.closing_time

    if exception:
        if exception.opening_time is not None:
            opening_time = exception.opening_time
        if exception.closing_time is not None:
            closing_time = exception.closing_time

    if opening_time >= closing_time:
        return None

    return (
        datetime.combine(target_date, opening_time),
        datetime.combine(target_date, closing_time),
    )


def _get_slots_for_professional(
    establishment_id: int,
    service: Service,
    target_date: date,
    start_datetime: datetime,
    end_datetime: datetime,
    professional_id: int | None,
    exclude_appointment_id: int | None = None,
):
    appointments_query = Appointment.query.filter(
        Appointment.establishment_id == establishment_id,
        Appointment.starts_at < end_datetime,
        Appointment.ends_at > start_datetime,
        Appointment.status != "cancelled",
    )

    if professional_id is not None:
        appointments_query = appointments_query.filter(
            Appointment.professional_id == professional_id
        )

    if exclude_appointment_id is not None:
        appointments_query = appointments_query.filter(
            Appointment.id != exclude_appointment_id
        )

    appointments = appointments_query.all()

    busy_ranges = [
        (to_naive(appointment.starts_at), to_naive(appointment.ends_at))
        for appointment in appointments
    ]

    slots = []
    current = start_datetime
    duration = timedelta(minutes=service.duration_minutes)

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


def get_available_slots(
    establishment_id: int,
    service_id: int,
    target_date: date,
    exclude_appointment_id: int | None = None,
    professional_id: int | None = None,
):
    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        return []

    schedule_window = _get_schedule_window(
        establishment_id,
        target_date,
    )

    if not schedule_window:
        return []

    start_datetime, end_datetime = schedule_window

    if professional_id is not None:
        professional = Professional.query.filter_by(
            id=professional_id,
            establishment_id=establishment_id,
            active=True,
        ).first()

        if not professional or professional not in service.professionals:
            return []

        return _get_slots_for_professional(
            establishment_id=establishment_id,
            service=service,
            target_date=target_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            professional_id=professional.id,
            exclude_appointment_id=exclude_appointment_id,
        )

    professionals = [
        professional
        for professional in service.professionals
        if professional.active and professional.establishment_id == establishment_id
    ]

    # Compatibilidade com estabelecimentos que ainda não usam profissionais.
    if not professionals:
        return _get_slots_for_professional(
            establishment_id=establishment_id,
            service=service,
            target_date=target_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            professional_id=None,
            exclude_appointment_id=exclude_appointment_id,
        )

    # Sem preferência: retorna horários disponíveis para pelo menos
    # um profissional, sem deixar a agenda de outro bloquear esse horário.
    available_slots = set()

    for professional in professionals:
        slots = _get_slots_for_professional(
            establishment_id=establishment_id,
            service=service,
            target_date=target_date,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            professional_id=professional.id,
            exclude_appointment_id=exclude_appointment_id,
        )
        available_slots.update(slots)

    return sorted(available_slots)
