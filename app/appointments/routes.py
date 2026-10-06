from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from app.core.availability import get_available_slots, to_naive
from app.core.errors import APIError
from app.extensions import db
from app.models import Appointment, Service
from app.auth.decorators import jwt_required_with_user
from app.auth.context import get_current_establishment_id
from app.appointments.validation import (
    validate_appointment_payload,
)

appointments_bp = Blueprint(
    "appointments",
    __name__,
    url_prefix="/appointments",
)


def serialize_appointment(appointment):
    return {
        "id": appointment.id,
        "establishment_id": appointment.establishment_id,
        "service_id": appointment.service_id,
        "customer_name": appointment.customer_name,
        "customer_phone": appointment.customer_phone,
        "starts_at": to_naive(appointment.starts_at).isoformat(),
        "ends_at": to_naive(appointment.ends_at).isoformat(),
        "status": appointment.status,
    }


def parse_datetime(value):
    # Sempre trabalhamos com datetimes naive (UTC) na aplicação.
    return to_naive(datetime.fromisoformat(value))


def is_slot_available(
    establishment_id,
    service_id,
    starts_at,
    exclude_appointment_id=None,
):
    starts_at = to_naive(starts_at)

    available_slots = get_available_slots(
        establishment_id=establishment_id,
        service_id=service_id,
        target_date=starts_at.date(),
        exclude_appointment_id=exclude_appointment_id,
    )

    return any(slot == starts_at for slot in available_slots)


@appointments_bp.post("")
@jwt_required_with_user
def create_appointment():
    data = request.get_json(silent=True) or {}
    data["establishment_id"] = get_current_establishment_id()

    errors = validate_appointment_payload(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    service = Service.query.filter_by(
        id=data["service_id"],
        establishment_id=data["establishment_id"],
        active=True,
    ).first()

    if not service:
        raise APIError(
            "Service not found",
            status_code=404,
        )

    starts_at = parse_datetime(data["starts_at"])

    ends_at = starts_at + timedelta(minutes=service.duration_minutes)

    slot_is_available = is_slot_available(
        establishment_id=get_current_establishment_id(),
        service_id=data["service_id"],
        starts_at=starts_at,
    )

    if not slot_is_available:
        raise APIError(
            "Selected time slot is not available",
            status_code=409,
        )

    appointment = Appointment(
        establishment_id=data["establishment_id"],
        service_id=data["service_id"],
        customer_name=data["customer_name"].strip(),
        customer_phone=data["customer_phone"].strip(),
        starts_at=starts_at,
        ends_at=ends_at,
        status="scheduled",
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify(serialize_appointment(appointment)), 201


@appointments_bp.get("")
@jwt_required_with_user
def list_appointments():
    establishment_id = get_current_establishment_id()

    appointments = (
        Appointment.query.filter_by(
            establishment_id=establishment_id,
        )
        .order_by(Appointment.starts_at)
        .all()
    )

    return jsonify([serialize_appointment(appointment) for appointment in appointments])


@appointments_bp.get("/<int:appointment_id>")
@jwt_required_with_user
def get_appointment(appointment_id):
    establishment_id = get_current_establishment_id()

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        establishment_id=establishment_id,
    ).first()

    if not appointment:
        raise APIError(
            "Appointment not found",
            status_code=404,
        )

    return jsonify(serialize_appointment(appointment))


@appointments_bp.put("/<int:appointment_id>")
@jwt_required_with_user
def update_appointment(appointment_id):
    establishment_id = get_current_establishment_id()

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        establishment_id=establishment_id,
    ).first()

    if not appointment:
        raise APIError(
            "Appointment not found",
            status_code=404,
        )

    data = request.get_json(silent=True)

    errors = validate_appointment_payload(
        data,
        partial=True,
    )

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    if "customer_name" in data:
        appointment.customer_name = data["customer_name"].strip()

    if "customer_phone" in data:
        appointment.customer_phone = data["customer_phone"].strip()

    new_status = data["status"] if "status" in data else appointment.status

    if new_status not in {
        "scheduled",
        "cancelled",
    }:
        raise APIError(
            "Validation error",
            status_code=400,
            details={"status": ("Must be scheduled or cancelled")},
        )

    new_starts_at = (
        parse_datetime(data["starts_at"])
        if "starts_at" in data
        else to_naive(appointment.starts_at)
    )

    # Busca o serviço atual do agendamento.
    service = Service.query.filter_by(
        id=appointment.service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        raise APIError(
            "Service not found",
            status_code=404,
        )

    new_ends_at = new_starts_at + timedelta(minutes=service.duration_minutes)

    # Se o agendamento ficará como scheduled,
    # precisamos garantir que o horário final esteja
    # disponível.
    if new_status == "scheduled":
        slot_is_available = is_slot_available(
            establishment_id=establishment_id,
            service_id=appointment.service_id,
            starts_at=new_starts_at,
            exclude_appointment_id=appointment.id,
        )

        if not slot_is_available:
            raise APIError(
                "Selected time slot is not available",
                status_code=409,
            )

    appointment.starts_at = new_starts_at
    appointment.ends_at = new_ends_at
    appointment.status = new_status

    db.session.commit()

    return jsonify(serialize_appointment(appointment))


@appointments_bp.delete("/<int:appointment_id>")
@jwt_required_with_user
def cancel_appointment(appointment_id):
    establishment_id = get_current_establishment_id()

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        establishment_id=establishment_id,
    ).first()

    if not appointment:
        raise APIError(
            "Appointment not found",
            status_code=404,
        )

    appointment.status = "cancelled"

    db.session.commit()

    return jsonify({"message": "Appointment cancelled successfully"})
