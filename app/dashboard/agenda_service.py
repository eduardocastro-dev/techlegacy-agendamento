from datetime import date, datetime

from app.extensions import db
from app.models import (
    Appointment,
    Schedule,
    ScheduleException,
)


def get_agenda_data(establishment_id, target_date):
    """
    Retorna os dados da agenda de um estabelecimento
    para uma data específica.
    """

    weekday = target_date.weekday()

    # 1. Busca o horário normal do estabelecimento
    schedule = Schedule.query.filter_by(
        establishment_id=establishment_id,
        weekday=weekday,
        active=True,
    ).first()

    # 2. Busca uma possível exceção para a data
    exception = ScheduleException.query.filter_by(
        establishment_id=establishment_id,
        date=target_date,
    ).first()

    # 3. Se existe exceção de fechamento,
    # o estabelecimento não possui horário disponível.
    if exception and exception.closed:
        opening_time = None
        closing_time = None
        closed = True

    elif schedule:
        opening_time = schedule.opening_time
        closing_time = schedule.closing_time
        closed = False

        # 4. A exceção pode alterar o horário normal
        if exception:
            if exception.opening_time is not None:
                opening_time = exception.opening_time

            if exception.closing_time is not None:
                closing_time = exception.closing_time

    else:
        opening_time = None
        closing_time = None
        closed = True

    # 5. Busca os agendamentos do dia
    start_datetime = (
        datetime.combine(
            target_date,
            opening_time,
        )
        if opening_time
        else datetime.combine(
            target_date,
            datetime.min.time(),
        )
    )

    end_datetime = (
        datetime.combine(
            target_date,
            closing_time,
        )
        if closing_time
        else datetime.combine(
            target_date,
            datetime.max.time(),
        )
    )

    appointments = (
        Appointment.query.filter(
            Appointment.establishment_id == establishment_id,
            Appointment.starts_at >= start_datetime,
            Appointment.starts_at <= end_datetime,
        )
        .order_by(Appointment.starts_at.asc())
        .all()
    )

    return {
        "date": target_date,
        "weekday": weekday,
        "schedule": {
            "opening_time": opening_time,
            "closing_time": closing_time,
            "closed": closed,
        },
        "appointments": appointments,
    }
