from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import Establishment, User


def get_establishment_settings(establishment_id):
    return db.session.get(
        Establishment,
        establishment_id,
    )


def update_establishment_settings(
    establishment,
    data,
):
    if "name" in data:
        establishment.name = data["name"].strip()

    if "phone" in data:
        phone = data["phone"]

        if phone is not None:
            phone = phone.strip()

        establishment.phone = phone

    if "slug" in data:
        establishment.slug = data["slug"].strip()

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        raise ValueError("Slug already exists")

    return establishment


# ============================================================
# Conta
# ============================================================


def get_user_account(user):
    return user


def update_user_account(user, data):
    new_email = data["email"].strip().lower()

    existing_user = User.query.filter(
        User.email == new_email,
        User.id != user.id,
    ).first()

    if existing_user:
        raise ValueError("Email already registered")

    user.email = new_email

    db.session.commit()

    return user


def update_user_password(user, current_password, new_password):
    if not check_password_hash(
        user.password_hash,
        current_password,
    ):
        raise ValueError("Current password is incorrect")

    user.password_hash = generate_password_hash(new_password)

    db.session.commit()

    return user
