from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import User


def get_current_user():
    """Obtém o usuário associado ao JWT autenticado."""

    user_id = get_jwt_identity()

    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError, OverflowError):
        return None

    if user_id <= 0:
        return None

    return db.session.get(User, user_id)


def get_current_establishment_id():
    """Obtém o estabelecimento do usuário autenticado."""

    user = get_current_user()

    if user is None:
        return None

    return user.establishment_id
