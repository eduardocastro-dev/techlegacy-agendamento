from sqlalchemy import func

from app.extensions import db


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    establishment_id = db.Column(
        db.Integer,
        db.ForeignKey("establishments.id"),
        nullable=False,
    )

    weekday = db.Column(
        db.Integer,
        nullable=False,
    )

    opening_time = db.Column(
        db.Time,
        nullable=False,
    )

    closing_time = db.Column(
        db.Time,
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
            "schedules",
            lazy=True,
        ),
    )

    def __repr__(self):
        return (
            f"<Schedule "
            f"establishment={self.establishment_id} "
            f"weekday={self.weekday}>"
        )
