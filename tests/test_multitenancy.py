from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Appointment, Establishment, Professional, Service, User


def create_second_establishment(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento B",
            slug="estabelecimento-b",
            phone="11888888888",
        )
        db.session.add(establishment)
        db.session.flush()

        user = User(
            establishment_id=establishment.id,
            email="usuario-b@exemplo.com",
            password_hash=generate_password_hash("senha-segura-123"),
        )
        db.session.add(user)
        db.session.commit()

        return establishment.id


def test_cannot_update_professional_from_another_establishment(
    app, client, establishment, auth_headers
):
    second_establishment_id = create_second_establishment(app)

    with app.app_context():
        professional = Professional(
            establishment_id=second_establishment_id,
            name="Profissional B",
            active=True,
        )
        db.session.add(professional)
        db.session.commit()
        professional_id = professional.id

    response = client.put(
        f"/professionals/{professional_id}",
        headers=auth_headers,
        json={"name": "Nome alterado indevidamente"},
    )

    assert response.status_code == 404

    with app.app_context():
        professional = db.session.get(Professional, professional_id)
        assert professional.name == "Profissional B"


def test_cannot_deactivate_professional_from_another_establishment(
    app, client, auth_headers
):
    second_establishment_id = create_second_establishment(app)

    with app.app_context():
        professional = Professional(
            establishment_id=second_establishment_id,
            name="Profissional B",
            active=True,
        )
        db.session.add(professional)
        db.session.commit()
        professional_id = professional.id

    response = client.delete(
        f"/professionals/{professional_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404

    with app.app_context():
        professional = db.session.get(Professional, professional_id)
        assert professional.active is True


def test_cannot_associate_service_from_another_establishment(app, client, auth_headers):
    second_establishment_id = create_second_establishment(app)

    with app.app_context():
        service = Service(
            establishment_id=second_establishment_id,
            name="Serviço B",
            duration_minutes=30,
            price=50,
            active=True,
        )
        db.session.add(service)
        db.session.commit()
        service_id = service.id

    response = client.post(
        "/professionals",
        headers=auth_headers,
        json={
            "name": "Profissional A",
            "active": True,
            "service_ids": [service_id],
        },
    )

    assert response.status_code == 400


def test_cannot_access_appointment_from_another_establishment(
    app, client, auth_headers
):
    second_establishment_id = create_second_establishment(app)

    with app.app_context():
        service = Service(
            establishment_id=second_establishment_id,
            name="Serviço B",
            duration_minutes=30,
            price=50,
            active=True,
        )
        db.session.add(service)
        db.session.flush()

        starts_at = datetime(2026, 11, 10, 10, 0)

        appointment = Appointment(
            establishment_id=second_establishment_id,
            service_id=service.id,
            professional_id=None,
            customer_name="Cliente B",
            customer_phone="11999999999",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=30),
            status="scheduled",
        )

        db.session.add(appointment)
        db.session.commit()
        appointment_id = appointment.id

    response_get = client.get(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
    )

    response_put = client.put(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
        json={"customer_name": "Alteração indevida"},
    )

    response_delete = client.delete(
        f"/appointments/{appointment_id}",
        headers=auth_headers,
    )

    assert response_get.status_code == 404
    assert response_put.status_code == 404
    assert response_delete.status_code == 404

    with app.app_context():
        appointment = db.session.get(
            Appointment,
            appointment_id,
        )

        assert appointment.customer_name == "Cliente B"
        assert appointment.status == "scheduled"
