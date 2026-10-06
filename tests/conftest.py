import pytest

from app import create_app
from app.extensions import db
from app.models import Establishment, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": (
                "postgresql+psycopg://"
                "agenda_user:agenda_password"
                "@localhost:5432/agenda_test"
            ),
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def establishment(app):
    with app.app_context():
        establishment = Establishment(
            name="Estabelecimento Teste",
            slug="estabelecimento-teste",
            phone="11999999999",
        )

        db.session.add(establishment)
        db.session.commit()

        establishment_id = establishment.id

        return establishment_id


@pytest.fixture
def user(app, establishment):
    with app.app_context():
        user = User(
            establishment_id=establishment,
            email="teste@exemplo.com",
            password_hash=generate_password_hash("123456"),
        )

        db.session.add(user)
        db.session.commit()

        return user.id


@pytest.fixture
def auth_headers(client, user):
    response = client.post(
        "/auth/login",
        json={
            "email": "teste@exemplo.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    return {"Authorization": f"Bearer {data['access_token']}"}
