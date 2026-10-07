from datetime import datetime, timedelta

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Appointment, Establishment, Service, User


def create_service(establishment_id):
    service = Service(
        establishment_id=establishment_id,
        name="Corte de cabelo",
        description="Corte masculino",
        duration_minutes=30,
        price=50.00,
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    return service.id


def create_appointment(
    establishment_id,
    service_id,
    starts_at,
    customer_name="João da Silva",
    customer_phone="11999999999",
    status="scheduled",
):
    appointment = Appointment(
        establishment_id=establishment_id,
        service_id=service_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(minutes=30),
        status=status,
    )

    db.session.add(appointment)
    db.session.commit()

    appointment_id = appointment.id

    return appointment_id


def test_dashboard_authenticated(
    client,
    auth_headers,
    establishment,
):
    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["establishment"]["id"] == establishment
    assert data["establishment"]["name"] == "Estabelecimento Teste"
    assert data["establishment"]["slug"] == "estabelecimento-teste"


def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard")

    assert response.status_code == 401


def test_dashboard_counts_today_appointments(
    app,
    client,
    auth_headers,
    establishment,
):
    with app.app_context():
        service_id = create_service(establishment)

        today = datetime.now().replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        create_appointment(
            establishment,
            service_id,
            today,
            customer_name="Cliente 1",
        )

        create_appointment(
            establishment,
            service_id,
            today + timedelta(hours=1),
            customer_name="Cliente 2",
        )

    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["summary"]["appointments_today"] == 2


def test_dashboard_counts_only_scheduled_appointments(
    app,
    client,
    auth_headers,
    establishment,
):
    with app.app_context():
        service_id = create_service(establishment)

        today = datetime.now().replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        create_appointment(
            establishment,
            service_id,
            today,
            customer_name="Agendado",
            status="scheduled",
        )

        create_appointment(
            establishment,
            service_id,
            today + timedelta(hours=1),
            customer_name="Cancelado",
            status="cancelled",
        )

    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["summary"]["appointments_today"] == 1


def test_dashboard_returns_upcoming_appointments(
    app,
    client,
    auth_headers,
    establishment,
):
    with app.app_context():
        service_id = create_service(establishment)

        now = datetime.now().replace(
            second=0,
            microsecond=0,
        )

        appointment_1 = create_appointment(
            establishment,
            service_id,
            now + timedelta(hours=2),
            customer_name="Cliente 1",
        )

        appointment_2 = create_appointment(
            establishment,
            service_id,
            now + timedelta(hours=1),
            customer_name="Cliente 2",
        )

    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["summary"]["upcoming_appointments"] == 2

    assert data["upcoming"][0]["id"] == appointment_2
    assert data["upcoming"][1]["id"] == appointment_1


def test_dashboard_limits_upcoming_to_five(
    app,
    client,
    auth_headers,
    establishment,
):
    with app.app_context():
        service_id = create_service(establishment)

        now = datetime.now().replace(
            second=0,
            microsecond=0,
        )

        for index in range(6):
            create_appointment(
                establishment,
                service_id,
                now + timedelta(hours=index + 1),
                customer_name=f"Cliente {index + 1}",
            )

    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["summary"]["upcoming_appointments"] == 5
    assert len(data["upcoming"]) == 5


def test_dashboard_returns_service_information(
    app,
    client,
    auth_headers,
    establishment,
):
    with app.app_context():
        service_id = create_service(establishment)

        now = datetime.now() + timedelta(hours=1)

        create_appointment(
            establishment,
            service_id,
            now,
            customer_name="Cliente",
        )

    response = client.get(
        "/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.get_json()

    appointment = data["upcoming"][0]

    assert appointment["service_id"] == service_id
    assert appointment["service_name"] == "Corte de cabelo"
    assert appointment["customer_name"] == "Cliente"
    assert appointment["customer_phone"] == "11999999999"
    assert appointment["status"] == "scheduled"


def test_dashboard_isolates_establishments(
    app,
    client,
    establishment,
    user,
):
    with app.app_context():
        # Estabelecimento A já existe através do fixture.
        service_a_id = create_service(establishment)

        now = datetime.now().replace(
            second=0,
            microsecond=0,
        )

        appointment_a_id = create_appointment(
            establishment,
            service_a_id,
            now + timedelta(hours=1),
            customer_name="Cliente Estabelecimento A",
        )

        # Cria Estabelecimento B.
        establishment_b = Establishment(
            name="Outro Estabelecimento",
            slug="outro-estabelecimento",
            phone="11888888888",
        )

        db.session.add(establishment_b)
        db.session.commit()

        establishment_b_id = establishment_b.id

        # Cria serviço do Estabelecimento B.
        service_b_id = create_service(establishment_b_id)

        # Cria agendamento do Estabelecimento B.
        appointment_b_id = create_appointment(
            establishment_b_id,
            service_b_id,
            now + timedelta(hours=2),
            customer_name="Cliente Estabelecimento B",
        )

        # Cria usuário do Estabelecimento B.
        user_b = User(
            establishment_id=establishment_b_id,
            email="outro@exemplo.com",
            password_hash=generate_password_hash("123456"),
        )

        db.session.add(user_b)
        db.session.commit()

        token_a = create_access_token(identity=str(user))

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert response.status_code == 200

    data = response.get_json()

    upcoming_ids = [appointment["id"] for appointment in data["upcoming"]]

    assert appointment_a_id in upcoming_ids
    assert appointment_b_id not in upcoming_ids

    assert data["establishment"]["id"] == establishment
