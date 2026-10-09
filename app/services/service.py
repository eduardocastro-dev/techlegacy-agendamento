from app.extensions import db
from app.models import Service


def create_service(
    establishment_id,
    name,
    description,
    duration_minutes,
    price,
):
    service = Service(
        establishment_id=establishment_id,
        name=name.strip(),
        description=description,
        duration_minutes=duration_minutes,
        price=price,
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    return service


def list_services(establishment_id, include_inactive=False):
    query = Service.query.filter_by(
        establishment_id=establishment_id,
    )

    # Por padrão só os ativos (ex.: página pública de agendamento).
    if not include_inactive:
        query = query.filter_by(active=True)

    return query.order_by(Service.id).all()


def get_service(establishment_id, service_id, include_inactive=False):
    query = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment_id,
    )
    if not include_inactive:
        query = query.filter_by(active=True)
    return query.first()


def update_service(
    service,
    data,
):
    if "name" in data:
        service.name = data["name"].strip()

    if "description" in data:
        service.description = data["description"]

    if "duration_minutes" in data:
        service.duration_minutes = data["duration_minutes"]

    if "price" in data:
        service.price = data["price"]

    db.session.commit()

    return service


def deactivate_service(service):
    service.active = False

    db.session.commit()

    return service


def activate_service(service):
    service.active = True
    db.session.commit()
    return service
