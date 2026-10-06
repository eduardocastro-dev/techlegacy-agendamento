from datetime import datetime

from flask import Blueprint, jsonify, request

from app.auth.context import get_current_establishment_id
from app.auth.decorators import jwt_required_with_user
from app.core.errors import APIError
from app.extensions import db
from app.models import Schedule
from app.schedules.validation import validate_schedule_payload

schedules_bp = Blueprint(
    "schedules",
    __name__,
    url_prefix="/schedules",
)


def serialize_schedule(schedule):
    return {
        "id": schedule.id,
        "establishment_id": schedule.establishment_id,
        "weekday": schedule.weekday,
        "opening_time": schedule.opening_time.strftime("%H:%M"),
        "closing_time": schedule.closing_time.strftime("%H:%M"),
        "active": schedule.active,
    }


def parse_time(value):
    return datetime.strptime(
        value,
        "%H:%M",
    ).time()


@schedules_bp.post("")
@jwt_required_with_user
def create_schedule():
    data = request.get_json(silent=True)

    errors = validate_schedule_payload(data)

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    establishment_id = get_current_establishment_id()

    existing_schedule = Schedule.query.filter_by(
        establishment_id=establishment_id,
        weekday=data["weekday"],
        active=True,
    ).first()

    if existing_schedule:
        raise APIError(
            "Schedule already exists for this weekday",
            status_code=409,
        )

    schedule = Schedule(
        establishment_id=establishment_id,
        weekday=data["weekday"],
        opening_time=parse_time(data["opening_time"]),
        closing_time=parse_time(data["closing_time"]),
        active=True,
    )

    db.session.add(schedule)
    db.session.commit()

    return jsonify(serialize_schedule(schedule)), 201


@schedules_bp.get("")
@jwt_required_with_user
def list_schedules():
    establishment_id = get_current_establishment_id()

    schedules = (
        Schedule.query.filter_by(
            establishment_id=establishment_id,
            active=True,
        )
        .order_by(Schedule.weekday)
        .all()
    )

    return jsonify([serialize_schedule(schedule) for schedule in schedules])


@schedules_bp.get("/<int:schedule_id>")
@jwt_required_with_user
def get_schedule(schedule_id):
    establishment_id = get_current_establishment_id()

    schedule = Schedule.query.filter_by(
        id=schedule_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not schedule:
        raise APIError(
            "Schedule not found",
            status_code=404,
        )

    return jsonify(serialize_schedule(schedule))


@schedules_bp.put("/<int:schedule_id>")
@jwt_required_with_user
def update_schedule(schedule_id):
    establishment_id = get_current_establishment_id()

    schedule = Schedule.query.filter_by(
        id=schedule_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not schedule:
        raise APIError(
            "Schedule not found",
            status_code=404,
        )

    data = request.get_json(silent=True)

    errors = validate_schedule_payload(
        data,
        partial=True,
    )

    if errors:
        raise APIError(
            "Validation error",
            status_code=400,
            details=errors,
        )

    new_weekday = data.get(
        "weekday",
        schedule.weekday,
    )

    duplicate = Schedule.query.filter(
        Schedule.id != schedule.id,
        Schedule.establishment_id == establishment_id,
        Schedule.weekday == new_weekday,
        Schedule.active.is_(True),
    ).first()

    if duplicate:
        raise APIError(
            "Schedule already exists for this weekday",
            status_code=409,
        )

    if "weekday" in data:
        schedule.weekday = data["weekday"]

    if "opening_time" in data:
        schedule.opening_time = parse_time(data["opening_time"])

    if "closing_time" in data:
        schedule.closing_time = parse_time(data["closing_time"])

    db.session.commit()

    return jsonify(serialize_schedule(schedule))


@schedules_bp.delete("/<int:schedule_id>")
@jwt_required_with_user
def delete_schedule(schedule_id):
    establishment_id = get_current_establishment_id()

    schedule = Schedule.query.filter_by(
        id=schedule_id,
        establishment_id=establishment_id,
        active=True,
    ).first()

    if not schedule:
        raise APIError(
            "Schedule not found",
            status_code=404,
        )

    schedule.active = False

    db.session.commit()

    return jsonify({"message": "Schedule deactivated successfully"})
