from flask_jwt_extended import get_jwt_identity
from app.models import User


def get_current_user():
    user_id = get_jwt_identity()

    if not user_id:
        return None

    return User.query.get(int(user_id))


def get_current_establishment_id():
    user = get_current_user()

    if not user:
        return None

    return user.establishment_id