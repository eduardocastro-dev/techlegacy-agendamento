from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from app.auth.context import get_current_establishment_id
from app.auth.decorators import jwt_required_with_user

from .agenda_service import get_agenda_data
from .service import get_dashboard_data

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
)


@dashboard_bp.get("/admin")
def admin_dashboard():
    return render_template("dashboard/index.html")


@dashboard_bp.get("/admin/agenda")
def admin_agenda():
    return render_template("dashboard/agenda.html")


@dashboard_bp.get("/admin/profissionais")
def admin_professionals():
    return render_template("dashboard/profissionais.html")


@dashboard_bp.get("/admin/servicos")
def admin_services():
    return render_template("dashboard/services.html")


@dashboard_bp.get("/admin/horarios")
def admin_schedules():
    return render_template("dashboard/horarios.html")


@dashboard_bp.get("/admin/configuracoes")
def admin_settings():
    return render_template("dashboard/configuracoes.html")


def serialize_appointment(appointment):
    return {
        "id": appointment.id,
        "service_id": appointment.service_id,
        "service_name": (appointment.service.name if appointment.service else None),
        "professional_id": appointment.professional_id,
        "professional_name": (
            appointment.professional.name
            if appointment.professional
            else None
        ),
        "customer_name": appointment.customer_name,
        "customer_phone": appointment.customer_phone,
        "starts_at": appointment.starts_at.isoformat(),
        "ends_at": appointment.ends_at.isoformat(),
        "status": appointment.status,
    }


@dashboard_bp.get("")
@jwt_required_with_user
def dashboard():
    establishment_id = get_current_establishment_id()

    dashboard_data = get_dashboard_data(establishment_id)

    if not dashboard_data:
        return jsonify({"error": "Establishment not found"}), 404

    establishment = dashboard_data["establishment"]
    upcoming_appointments = dashboard_data["upcoming_appointments"]

    return jsonify(
        {
            "establishment": {
                "id": establishment.id,
                "name": establishment.name,
                "slug": establishment.slug,
            },
            "summary": {
                "appointments_today": dashboard_data["appointments_today"],
                "upcoming_appointments": len(upcoming_appointments),
                "active_services": dashboard_data["active_services"],
                "professionals": dashboard_data["professionals"],
            },
            "upcoming": [
                serialize_appointment(appointment)
                for appointment in upcoming_appointments
            ],
        }
    )


@dashboard_bp.get("/agenda")
@jwt_required_with_user
def agenda():
    establishment_id = get_current_establishment_id()

    date_param = request.args.get("date")

    if not date_param:
        return jsonify({"error": "Query parameter 'date' is required"}), 400

    try:
        target_date = datetime.strptime(
            date_param,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    agenda_data = get_agenda_data(
        establishment_id,
        target_date,
    )

    if not agenda_data:
        return jsonify({"error": "Agenda not found"}), 404

    schedule = agenda_data["schedule"]

    return jsonify(
        {
            "date": agenda_data["date"].isoformat(),
            "weekday": agenda_data["weekday"],
            "schedule": {
                "opening_time": (
                    schedule["opening_time"].strftime("%H:%M")
                    if schedule["opening_time"]
                    else None
                ),
                "closing_time": (
                    schedule["closing_time"].strftime("%H:%M")
                    if schedule["closing_time"]
                    else None
                ),
                "closed": schedule["closed"],
            },
            "appointments": [
                serialize_appointment(appointment)
                for appointment in agenda_data["appointments"]
            ],
        }
    )
