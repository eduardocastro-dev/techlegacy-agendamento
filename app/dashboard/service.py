from datetime import datetime

from app.extensions import db
from app.models import Appointment, Establishment, Professional, Service


def get_dashboard_data(establishment_id):
    establishment = db.session.get(
        Establishment,
        establishment_id,
    )

    if not establishment:
        return None

    now = datetime.now()
    today = now.date()

    appointments_today = Appointment.query.filter(
        Appointment.establishment_id == establishment_id,
        db.func.date(Appointment.starts_at) == today,
        Appointment.status == "scheduled",
    ).count()

    upcoming_appointments = (
        Appointment.query.filter(
            Appointment.establishment_id == establishment_id,
            Appointment.starts_at >= now,
            Appointment.status == "scheduled",
        )
        .order_by(Appointment.starts_at.asc())
        .limit(5)
        .all()
    )

    professionals = Professional.query.filter_by(
        establishment_id=establishment_id,
    ).count()

    active_services = Service.query.filter_by(
        establishment_id=establishment_id,
        active=True,
    ).count()

    return {
        "establishment": establishment,
        "appointments_today": appointments_today,
        "upcoming_appointments": upcoming_appointments,
        "active_services": active_services,
        "professionals": professionals,
    }
