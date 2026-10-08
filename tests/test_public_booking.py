from app.extensions import db
from app.models import Service


def test_public_booking_page(client, establishment):
    service = Service(
        establishment_id=establishment,
        name="Corte masculino",
        description="Corte tradicional",
        duration_minutes=30,
        price=50.00,
        active=True,
    )

    db.session.add(service)
    db.session.commit()

    response = client.get("/agendamento/estabelecimento-teste")

    assert response.status_code == 200
    assert b"Estabelecimento Teste" in response.data
    assert b"Corte masculino" in response.data
    assert b"50,00" in response.data


def test_public_booking_page_not_found(client):
    response = client.get("/agendamento/estabelecimento-inexistente")

    assert response.status_code == 404
