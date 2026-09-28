from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Service


services_bp = Blueprint(
    "services",
    __name__,
    url_prefix="/services",
)


@services_bp.post("")
def create_service():
    data = request.get_json()

    service = Service(
        establishment_id=data["establishment_id"],
        name=data["name"],
        description=data.get("description"),
        duration_minutes=data["duration_minutes"],
        price=data["price"],
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    return jsonify({
        "id": service.id,
        "establishment_id": service.establishment_id,
        "name": service.name,
        "description": service.description,
        "duration_minutes": service.duration_minutes,
        "price": float(service.price),
        "active": service.active,
    }), 201


@services_bp.get("")
def list_services():
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    services = Service.query.filter_by(
        establishment_id=establishment_id,
        active=True,
    ).all()

    return jsonify([
        {
            "id": service.id,
            "establishment_id": service.establishment_id,
            "name": service.name,
            "description": service.description,
            "duration_minutes": service.duration_minutes,
            "price": float(service.price),
            "active": service.active,
        }
        for service in services
    ])

@services_bp.get("/<int:service_id>")
def get_service(service_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    return jsonify({
        "id": service.id,
        "establishment_id": service.establishment_id,
        "name": service.name,
        "description": service.description,
        "duration_minutes": service.duration_minutes,
        "price": float(service.price),
        "active": service.active,
    })

@services_bp.put("/<int:service_id>")
def update_service(service_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    data = request.get_json()

    if "name" in data:
        service.name = data["name"]

    if "description" in data:
        service.description = data["description"]

    if "duration_minutes" in data:
        service.duration_minutes = data["duration_minutes"]

    if "price" in data:
        service.price = data["price"]

    db.session.commit()

    return jsonify({
        "id": service.id,
        "establishment_id": service.establishment_id,
        "name": service.name,
        "description": service.description,
        "duration_minutes": service.duration_minutes,
        "price": float(service.price),
        "active": service.active,
    })

@services_bp.delete("/<int:service_id>")
def delete_service(service_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not service:
        return jsonify({
            "error": "Service not found"
        }), 404

    service.active = False

    db.session.commit()

    return jsonify({
        "message": "Service deactivated successfully"
    })