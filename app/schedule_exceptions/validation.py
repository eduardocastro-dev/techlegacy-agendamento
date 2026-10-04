from datetime import datetime


def validate_schedule_exception_payload(
    data,
    partial=False,
):
    if not isinstance(data, dict):
        return {
            "body": "Request body must be a JSON object"
        }

    errors = {}

    required_fields = [
        "establishment_id",
        "date",
    ]

    if not partial:
        for field in required_fields:
            if field not in data:
                errors[field] = "This field is required"

    if "establishment_id" in data:
        if not isinstance(data["establishment_id"], int):
            errors["establishment_id"] = (
                "Must be an integer"
            )

    if "date" in data:
        value = data["date"]

        if not isinstance(value, str):
            errors["date"] = (
                "Must be in YYYY-MM-DD format"
            )
        else:
            try:
                datetime.strptime(
                    value,
                    "%Y-%m-%d",
                )
            except ValueError:
                errors["date"] = (
                    "Must be in YYYY-MM-DD format"
                )

    for field in ["opening_time", "closing_time"]:
        if field in data and data[field] is not None:
            value = data[field]

            if not isinstance(value, str):
                errors[field] = (
                    "Must be a string in HH:MM format"
                )
                continue

            try:
                datetime.strptime(
                    value,
                    "%H:%M",
                )
            except ValueError:
                errors[field] = (
                    "Must be in HH:MM format"
                )

    if "closed" in data:
        if not isinstance(data["closed"], bool):
            errors["closed"] = "Must be a boolean"

    if (
        "opening_time" in data
        and "closing_time" in data
        and data["opening_time"] is not None
        and data["closing_time"] is not None
        and "opening_time" not in errors
        and "closing_time" not in errors
    ):
        opening = datetime.strptime(
            data["opening_time"],
            "%H:%M",
        ).time()

        closing = datetime.strptime(
            data["closing_time"],
            "%H:%M",
        ).time()

        if opening >= closing:
            errors["closing_time"] = (
                "Must be later than opening_time"
            )

    closed = data.get("closed", False)

    if (
        closed is False
        and "opening_time" in data
        and "closing_time" in data
    ):
        if (
            data["opening_time"] is None
            or data["closing_time"] is None
        ):
            errors["opening_time"] = (
                "Opening and closing times "
                "are required when closed is false"
            )

    return errors