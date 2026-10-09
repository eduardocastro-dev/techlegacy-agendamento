from flask import Blueprint, jsonify, request

from app.auth.context import (
    get_current_establishment_id,
    get_current_user,
)
from app.auth.decorators import jwt_required_with_user
from app.core.errors import APIError

from .service import (
    get_establishment_settings,
    update_establishment_settings,
    update_user_account,
    update_user_password,
)
from .validation import (
    validate_account_update,
    validate_establishment_update,
    validate_password_update,
)

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings",
)


def serialize_establishment(establishment):
    return {
        "id": establishment.id,
        "name": establishment.name,
        "slug": establishment.slug,
        "phone": establishment.phone,
        "trial_ends_at": (
            establishment.trial_ends_at.isoformat()
            if establishment.trial_ends_at
            else None
        ),
        "created_at": (
            establishment.created_at.isoformat() if establishment.created_at else None
        ),
    }


@settings_bp.get("")
@jwt_required_with_user
def get_settings():

    establishment_id = get_current_establishment_id()

    establishment = get_establishment_settings(establishment_id)

    if not establishment:
        raise APIError(
            "Establishment not found",
            status_code=404,
        )

    return jsonify(serialize_establishment(establishment))


@settings_bp.put("")
@jwt_required_with_user
def update_settings():

    establishment_id = get_current_establishment_id()

    establishment = get_establishment_settings(establishment_id)

    if not establishment:
        raise APIError(
            "Establishment not found",
            status_code=404,
        )

    data = request.get_json(silent=True)

    errors = validate_establishment_update(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    try:
        establishment = update_establishment_settings(
            establishment,
            data,
        )

    except ValueError as error:
        raise APIError(
            str(error),
            status_code=409,
        )

    return jsonify(serialize_establishment(establishment))


@settings_bp.get("/account")
@jwt_required_with_user
def get_account():

    user = get_current_user()

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "establishment_id": user.establishment_id,
            "created_at": (user.created_at.isoformat() if user.created_at else None),
        }
    )


@settings_bp.put("/account")
@jwt_required_with_user
def update_account():

    user = get_current_user()

    data = request.get_json(silent=True)

    errors = validate_account_update(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    try:
        user = update_user_account(
            user,
            data,
        )

    except ValueError as error:
        raise APIError(
            str(error),
            status_code=409,
        )

    return jsonify(
        {
            "id": user.id,
            "email": user.email,
            "establishment_id": user.establishment_id,
            "created_at": (user.created_at.isoformat() if user.created_at else None),
        }
    )


@settings_bp.put("/password")
@jwt_required_with_user
def update_password():

    user = get_current_user()

    data = request.get_json(silent=True)

    errors = validate_password_update(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    try:
        update_user_password(
            user,
            data["current_password"],
            data["new_password"],
        )

    except ValueError as error:
        raise APIError(
            str(error),
            status_code=401,
        )

    return jsonify({"message": "Password updated successfully"})
