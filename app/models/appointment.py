from sqlalchemy import func

from app.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    establishment_id = db.Column(
        db.Integer,
        db.ForeignKey("establishments.id"),
        nullable=False,
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id"),
        nullable=False,
    )

    customer_name = db.Column(
        db.String(120),
        nullable=False,
    )

    customer_phone = db.Column(
        db.String(20),
        nullable=False,
    )

    starts_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    ends_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="scheduled",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    establishment = db.relationship(
        "Establishment",
        backref=db.backref(
            "appointments",
            lazy=True,
        ),
    )

    service = db.relationship(
        "Service",
        backref=db.backref(
            "appointments",
            lazy=True,
        ),
    )

    def __repr__(self):
        return f"<Appointment " f"id={self.id} " f"customer={self.customer_name}>"
