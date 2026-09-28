from sqlalchemy import func

from app.extensions import db


class ScheduleException(db.Model):
    __tablename__ = "schedule_exceptions"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    establishment_id = db.Column(
        db.Integer,
        db.ForeignKey("establishments.id"),
        nullable=False,
    )

    date = db.Column(
        db.Date,
        nullable=False,
    )

    opening_time = db.Column(
        db.Time,
        nullable=True,
    )

    closing_time = db.Column(
        db.Time,
        nullable=True,
    )

    closed = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    establishment = db.relationship(
        "Establishment",
        backref=db.backref(
            "schedule_exceptions",
            lazy=True,
        ),
    )

    def __repr__(self):
        return (
            f"<ScheduleException "
            f"establishment={self.establishment_id} "
            f"date={self.date}>"
        )