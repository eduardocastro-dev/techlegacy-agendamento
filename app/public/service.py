
from app.core.availability import get_available_slots
from app.models import Establishment, Service


def get_public_establishment(slug):
    establishment = Establishment.query.filter_by(
        slug=slug,
    ).first()

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

    return {
        "establishment": establishment,
        "services": services,
    }


def get_public_availability(
    slug,
    service_id,
    target_date,
):
    establishment = Establishment.query.filter_by(
        slug=slug,
    ).first()

    if not establishment:
        return None

    service = Service.query.filter_by(
        id=service_id,
        establishment_id=establishment.id,
        active=True,
    ).first()

    if not service:
        return None

    slots = get_available_slots(
        establishment_id=establishment.id,
        service_id=service.id,
        target_date=target_date,
    )

    return {
        "establishment": establishment,
        "service": service,
        "date": target_date,
        "slots": slots,
    }
