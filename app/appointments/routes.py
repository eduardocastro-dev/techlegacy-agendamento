from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from app.core.availability import get_available_slots
from app.core.errors import APIError
from app.extensions import db
from app.models import Appointment, Service
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
        "starts_at": appointment.starts_at.isoformat(),
        "ends_at": appointment.ends_at.isoformat(),
        "status": appointment.status,
    }


def parse_datetime(value):
    return datetime.fromisoformat(value)


@appointments_bp.post("")
def create_appointment():
    data = request.get_json(silent=True)

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

    starts_at = parse_datetime(
        data["starts_at"]
    )

    ends_at = starts_at + timedelta(
        minutes=service.duration_minutes
    )

    available_slots = get_available_slots(
        establishment_id=data["establishment_id"],
        service_id=data["service_id"],
        target_date=starts_at.date(),
    )

    slot_is_available = any(
        slot == starts_at
        for slot in available_slots
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

    return jsonify(
        serialize_appointment(appointment)
    ), 201


@appointments_bp.get("")
def list_appointments():
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

    appointments = Appointment.query.filter_by(
        establishment_id=establishment_id,
    ).order_by(
        Appointment.starts_at
    ).all()

    return jsonify([
        serialize_appointment(appointment)
        for appointment in appointments
    ])


@appointments_bp.get("/<int:appointment_id>")
def get_appointment(appointment_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

    appointment = Appointment.query.filter_by(
        id=appointment_id,
        establishment_id=establishment_id,
    ).first()

    if not appointment:
        raise APIError(
            "Appointment not found",
            status_code=404,
        )

    return jsonify(
        serialize_appointment(appointment)
    )


@appointments_bp.put("/<int:appointment_id>")
def update_appointment(appointment_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

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
        appointment.customer_name = (
            data["customer_name"].strip()
        )

    if "customer_phone" in data:
        appointment.customer_phone = (
            data["customer_phone"].strip()
        )

    if "status" in data:
        allowed_statuses = {
            "scheduled",
            "cancelled",
        }

        if data["status"] not in allowed_statuses:
            raise APIError(
                "Validation error",
                status_code=400,
                details={
                    "status": (
                        "Must be scheduled or cancelled"
                    )
                },
            )

        appointment.status = data["status"]

    if "starts_at" in data:
        starts_at = parse_datetime(
            data["starts_at"]
        )

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

        available_slots = get_available_slots(
            establishment_id=establishment_id,
            service_id=appointment.service_id,
            target_date=starts_at.date(),
        )

        other_appointments = Appointment.query.filter(
            Appointment.id != appointment.id,
            Appointment.establishment_id
            == establishment_id,
            Appointment.starts_at
            < starts_at + timedelta(
                minutes=service.duration_minutes
            ),
            Appointment.ends_at > starts_at,
            Appointment.status != "cancelled",
        ).all()

        has_conflict = len(other_appointments) > 0

        if (
            starts_at not in available_slots
            or has_conflict
        ):
            raise APIError(
                "Selected time slot is not available",
                status_code=409,
            )

        appointment.starts_at = starts_at
        appointment.ends_at = (
            starts_at
            + timedelta(
                minutes=service.duration_minutes
            )
        )

    db.session.commit()

    return jsonify(
        serialize_appointment(appointment)
    )


@appointments_bp.delete("/<int:appointment_id>")
def cancel_appointment(appointment_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

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

    return jsonify({
        "message": "Appointment cancelled successfully"
    })