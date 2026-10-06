from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import Establishment, User

from .validation import (
    validate_login_payload,
    validate_register_payload,
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)

    error = validate_register_payload(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    email = data["email"].strip().lower()
    slug = data["slug"].strip().lower()

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already registered"
        }), 409

    existing_establishment = Establishment.query.filter_by(
        slug=slug
    ).first()

    if existing_establishment:
        return jsonify({
            "error": "Slug already registered"
        }), 409

    establishment = Establishment(
        name=data["establishment_name"].strip(),
        slug=slug,
        phone=data.get("phone"),
    )

    db.session.add(establishment)
    db.session.flush()

    user = User(
        establishment_id=establishment.id,
        email=email,
        password_hash=generate_password_hash(
            data["password"]
        ),
    )

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "establishment_id": user.establishment_id,
        },
        "establishment": {
            "id": establishment.id,
            "name": establishment.name,
            "slug": establishment.slug,
        },
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)

    error = validate_login_payload(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    email = data["email"].strip().lower()

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not check_password_hash(
        user.password_hash,
        data["password"],
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "establishment_id": user.establishment_id,
        },
    }), 200