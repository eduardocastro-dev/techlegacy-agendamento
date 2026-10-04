from flask import Blueprint, jsonify, request

from app.core.errors import APIError
from app.extensions import db
from app.models import Service
from app.services.validation import validate_service_payload


services_bp = Blueprint(
    "services",
    __name__,
    url_prefix="/services",
)


def serialize_service(service):
    return {
        "id": service.id,
        "establishment_id": service.establishment_id,
        "name": service.name,
        "description": service.description,
        "duration_minutes": service.duration_minutes,
        "price": float(service.price),
        "active": service.active,
    }


@services_bp.post("")
def create_service():
    data = request.get_json(silent=True)

    errors = validate_service_payload(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    service = Service(
        establishment_id=data["establishment_id"],
        name=data["name"].strip(),
        description=data.get("description"),
        duration_minutes=data["duration_minutes"],
        price=data["price"],
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    return jsonify(serialize_service(service)), 201


@services_bp.get("")
def list_services():
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": "This query parameter is required"
            },
        )

    services = Service.query.filter_by(
        establishment_id=establishment_id,
        active=True,
    ).all()

    return jsonify([
        serialize_service(service)
        for service in services
    ])


@services_bp.get("/<int:service_id>")
def get_service(service_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": "This query parameter is required"
            },
        )

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        raise APIError(
            "Service not found",
            status_code=404,
        )

    return jsonify(serialize_service(service))


@services_bp.put("/<int:service_id>")
def update_service(service_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": "This query parameter is required"
            },
        )

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        raise APIError(
            "Service not found",
            status_code=404,
        )

    data = request.get_json(silent=True)

    errors = validate_service_payload(
        data,
        partial=True,
    )

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    if "name" in data:
        service.name = data["name"].strip()

    if "description" in data:
        service.description = data["description"]

    if "duration_minutes" in data:
        service.duration_minutes = data["duration_minutes"]

    if "price" in data:
        service.price = data["price"]

    db.session.commit()

    return jsonify(serialize_service(service))


@services_bp.delete("/<int:service_id>")
def delete_service(service_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": "This query parameter is required"
            },
        )

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        raise APIError(
            "Service not found",
            status_code=404,
        )

    service.active = False

    db.session.commit()

    return jsonify({
        "message": "Service deactivated successfully"
    })