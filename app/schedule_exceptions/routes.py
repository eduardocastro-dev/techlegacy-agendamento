from datetime import datetime

from flask import Blueprint, jsonify, request

from app.core.errors import APIError
from app.extensions import db
from app.models import ScheduleException
from app.schedule_exceptions.validation import (
    validate_schedule_exception_payload,
)


schedule_exceptions_bp = Blueprint(
    "schedule_exceptions",
    __name__,
    url_prefix="/schedule-exceptions",
)


def serialize_schedule_exception(exception):
    return {
        "id": exception.id,
        "establishment_id": exception.establishment_id,
        "date": exception.date.isoformat(),
        "opening_time": (
            exception.opening_time.strftime("%H:%M")
            if exception.opening_time
            else None
        ),
        "closing_time": (
            exception.closing_time.strftime("%H:%M")
            if exception.closing_time
            else None
        ),
        "closed": exception.closed,
    }


def parse_date(value):
    return datetime.strptime(
        value,
        "%Y-%m-%d",
    ).date()


def parse_time(value):
    if value is None:
        return None

    return datetime.strptime(
        value,
        "%H:%M",
    ).time()


@schedule_exceptions_bp.post("")
def create_schedule_exception():
    data = request.get_json(silent=True)

    errors = validate_schedule_exception_payload(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    existing_exception = ScheduleException.query.filter_by(
        establishment_id=data["establishment_id"],
        date=parse_date(data["date"]),
    ).first()

    if existing_exception:
        raise APIError(
            "Schedule exception already exists for this date",
            status_code=409,
        )

    exception = ScheduleException(
        establishment_id=data["establishment_id"],
        date=parse_date(data["date"]),
        opening_time=parse_time(
            data.get("opening_time")
        ),
        closing_time=parse_time(
            data.get("closing_time")
        ),
        closed=data.get("closed", False),
    )

    db.session.add(exception)
    db.session.commit()

    return jsonify(
        serialize_schedule_exception(exception)
    ), 201


@schedule_exceptions_bp.get("")
def list_schedule_exceptions():
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

    exceptions = ScheduleException.query.filter_by(
        establishment_id=establishment_id,
    ).order_by(
        ScheduleException.date
    ).all()

    return jsonify([
        serialize_schedule_exception(exception)
        for exception in exceptions
    ])


@schedule_exceptions_bp.get(
    "/<int:exception_id>"
)
def get_schedule_exception(exception_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

    exception = ScheduleException.query.filter_by(
        id=exception_id,
        establishment_id=establishment_id,
    ).first()

    if not exception:
        raise APIError(
            "Schedule exception not found",
            status_code=404,
        )

    return jsonify(
        serialize_schedule_exception(exception)
    )


@schedule_exceptions_bp.put(
    "/<int:exception_id>"
)
def update_schedule_exception(exception_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

    exception = ScheduleException.query.filter_by(
        id=exception_id,
        establishment_id=establishment_id,
    ).first()

    if not exception:
        raise APIError(
            "Schedule exception not found",
            status_code=404,
        )

    data = request.get_json(silent=True)

    errors = validate_schedule_exception_payload(
        data,
        partial=True,
    )

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    new_date = parse_date(
        data["date"]
    ) if "date" in data else exception.date

    duplicate = ScheduleException.query.filter(
        ScheduleException.id != exception.id,
        ScheduleException.establishment_id == establishment_id,
        ScheduleException.date == new_date,
    ).first()

    if duplicate:
        raise APIError(
            "Schedule exception already exists for this date",
            status_code=409,
        )

    if "date" in data:
        exception.date = new_date

    if "opening_time" in data:
        exception.opening_time = parse_time(
            data["opening_time"]
        )

    if "closing_time" in data:
        exception.closing_time = parse_time(
            data["closing_time"]
        )

    if "closed" in data:
        exception.closed = data["closed"]

    db.session.commit()

    return jsonify(
        serialize_schedule_exception(exception)
    )


@schedule_exceptions_bp.delete(
    "/<int:exception_id>"
)
def delete_schedule_exception(exception_id):
    establishment_id = request.args.get(
        "establishment_id",
        type=int,
    )

    if establishment_id is None:
        raise APIError(
            "Validation error",
            status_code=400,
            details={
                "establishment_id": (
                    "This query parameter is required"
                )
            },
        )

    exception = ScheduleException.query.filter_by(
        id=exception_id,
        establishment_id=establishment_id,
    ).first()

    if not exception:
        raise APIError(
            "Schedule exception not found",
            status_code=404,
        )

    db.session.delete(exception)
    db.session.commit()

    return jsonify({
        "message": "Schedule exception deleted successfully"
    })