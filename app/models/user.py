from sqlalchemy import func

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    establishment_id = db.Column(
        db.Integer,
        db.ForeignKey("establishments.id"),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    establishment = db.relationship(
        "Establishment",
        backref=db.backref(
            "users",
            lazy=True,
        ),
    )

    def __repr__(self):
        return f"<User {self.email}>"