from app.core.availability import get_available_slots
from app.models import Establishment, Professional, Service


def get_public_establishment(slug):
    establishment = Establishment.query.filter_by(slug=slug).first()

    if not establishment:
        return None

    services = (
        Service.query.filter_by(
            establishment_id=establishment.id,
            active=True,
        )
        .order_by(Service.name.asc())
        .all()
    )

    service_professionals = {}
    for service in services:
        service_professionals[service.id] = [
            {"id": professional.id, "name": professional.name}
            for professional in service.professionals
            if professional.active and professional.establishment_id == establishment.id
        ]

    return {
        "establishment": establishment,
        "services": services,
        "service_professionals": service_professionals,
    }


def get_public_availability(
    slug,
    service_id,
    target_date,
    professional_id=None,
):
    establishment = Establishment.query.filter_by(slug=slug).first()

    if not establishment:
        return None

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment.id,
        active=True,
    ).first()

    if not service:
        return None

    professionals = [
        professional
        for professional in service.professionals
        if professional.active and professional.establishment_id == establishment.id
    ]

    selected_professional = None
    if professional_id is not None:
        selected_professional = Professional.query.filter_by(
            id=professional_id,
            establishment_id=establishment.id,
            active=True,
        ).first()
        if (
            not selected_professional
            or selected_professional not in service.professionals
        ):
            return None

    slots = get_available_slots(
        establishment_id=establishment.id,
        service_id=service.id,
        target_date=target_date,
        professional_id=professional_id,
    )

    return {
        "establishment": establishment,
        "service": service,
        "date": target_date,
        "slots": slots,
        "professionals": professionals,
        "professional": selected_professional,
    }
