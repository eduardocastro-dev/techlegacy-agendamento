from datetime import datetime
from sqlalchemy import func
from app.extensions import db


class Establishment(db.Model):
    __tablename__ = "establishments"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    slug = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(db.String(20))

    trial_ends_at = db.Column(
        db.DateTime(timezone=True)
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Establishment {self.name}>"