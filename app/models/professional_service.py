from sqlalchemy import Column, ForeignKey, Table

from app.extensions import db

professional_services = Table(
    "professional_services",
    db.metadata,
    Column(
        "professional_id",
        db.Integer,
        ForeignKey("professionals.id"),
        primary_key=True,
    ),
    Column(
        "service_id",
        db.Integer,
        ForeignKey("services.id"),
        primary_key=True,
    ),
)
