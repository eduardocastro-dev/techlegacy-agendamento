from flask import Blueprint, jsonify, request

from app.auth.context import get_current_establishment_id
from app.auth.decorators import jwt_required_with_user
from app.core.errors import APIError
from app.extensions import db
from app.models import Professional, Service
from app.professionals.validation import validate_professional_payload

professionals_bp = Blueprint("professionals", __name__, url_prefix="/professionals")


def serialize_professional(professional):
    return {
        "id": professional.id,
        "establishment_id": professional.establishment_id,
        "name": professional.name,
        "active": professional.active,
        "service_ids": [service.id for service in professional.services],
        "services": [service.name for service in professional.services],
        "created_at": (
            professional.created_at.isoformat() if professional.created_at else None
        ),
    }


def apply_service_ids(professional, service_ids, establishment_id):
    if not isinstance(service_ids, list):
        raise APIError(
            "Validation error",
            status_code=400,
            details={"service_ids": "Must be a list"},
        )
    services = (
        Service.query.filter(
            Service.establishment_id == establishment_id,
            Service.id.in_(service_ids),
            Service.active.is_(True),
        ).all()
        if service_ids
        else []
    )
    if len(services) != len(set(service_ids)):
        raise APIError(
            "One or more services were not found or are inactive", status_code=400
        )
    professional.services = services


@professionals_bp.post("")
@jwt_required_with_user
def create_professional():
    data = request.get_json(silent=True)
    errors = validate_professional_payload(data)
    if errors:
        raise APIError("Validation error", status_code=400, details=errors)

    establishment_id = get_current_establishment_id()
    professional = Professional(
        establishment_id=establishment_id,
        name=data["name"].strip(),
        active=data.get("active", True),
    )
    if "service_ids" in data:
        apply_service_ids(professional, data["service_ids"], establishment_id)
    db.session.add(professional)
    db.session.commit()
    return jsonify(serialize_professional(professional)), 201


@professionals_bp.get("")
@jwt_required_with_user
def list_professionals():
    establishment_id = get_current_establishment_id()
    include_inactive = request.args.get("include_inactive", "").lower() in (
        "1",
        "true",
        "yes",
    )
    query = Professional.query.filter_by(establishment_id=establishment_id)
    if not include_inactive:
        query = query.filter_by(active=True)
    professionals = query.order_by(Professional.name.asc()).all()
    return jsonify([serialize_professional(item) for item in professionals])


@professionals_bp.put("/<int:professional_id>")
@jwt_required_with_user
def update_professional(professional_id):
    establishment_id = get_current_establishment_id()
    professional = Professional.query.filter_by(
        id=professional_id, establishment_id=establishment_id
    ).first()
    if not professional:
        raise APIError("Professional not found", status_code=404)

    data = request.get_json(silent=True)
    errors = validate_professional_payload(data, partial=True)
    if errors:
        raise APIError("Validation error", status_code=400, details=errors)

    if "name" in data:
        professional.name = data["name"].strip()
    if "active" in data:
        professional.active = data["active"]
    if "service_ids" in data:
        apply_service_ids(professional, data["service_ids"], establishment_id)
    db.session.commit()
    return jsonify(serialize_professional(professional))


@professionals_bp.delete("/<int:professional_id>")
@jwt_required_with_user
def deactivate_professional(professional_id):
    establishment_id = get_current_establishment_id()
    professional = Professional.query.filter_by(
        id=professional_id, establishment_id=establishment_id
    ).first()
    if not professional:
        raise APIError("Professional not found", status_code=404)
    professional.active = False
    db.session.commit()
    return jsonify({"message": "Professional deactivated successfully"})
