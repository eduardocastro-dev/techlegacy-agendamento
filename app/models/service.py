from sqlalchemy import func
from app.extensions import db

class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    establishment_id = db.Column(
        db.Integer,
        db.ForeignKey("establishments.id"),
        nullable=False,
    )

    name = db.Column(
        db.String(120),
        nullable=False,
    )

    description = db.Column(
        db.Text,
    )

    duration_minutes = db.Column(
        db.Integer,
        nullable=False,
    )

    price = db.Column(
        db.Numeric(10, 2),
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
            "services",
            lazy=True,
        ),
    )

    def __repr__(self):
        return f"<Service {self.name}>"