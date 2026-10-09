from sqlalchemy import func

from app.extensions import db


class Professional(db.Model):
    __tablename__ = "professionals"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    establishment_id = db.Column(
        db.Integer,
        db.ForeignKey("establishments.id"),
        nullable=False,
    )

    name = db.Column(
        db.String(120),
        nullable=False,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    establishment = db.relationship(
        "Establishment",
        backref=db.backref(
            "professionals",
            lazy=True,
        ),
    )
    services = db.relationship(
        "Service",
        secondary="professional_services",
        back_populates="professionals",
        lazy=True,
    )

    def __repr__(self):
        return f"<Professional " f"id={self.id} " f"name={self.name}>"
