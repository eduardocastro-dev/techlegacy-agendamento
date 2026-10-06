from datetime import datetime


def validate_schedule_payload(data, partial=False):

    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object"}

    errors = {}

    required_fields = [
        "weekday",
        "opening_time",
        "closing_time",
    ]

    if not partial:
        for field in required_fields:
            if field not in data:
                errors[field] = "This field is required"

    if "weekday" in data:
        weekday = data["weekday"]

        if not isinstance(weekday, int) or isinstance(weekday, bool):
            errors["weekday"] = "Must be an integer"

        elif weekday < 0 or weekday > 6:
            errors["weekday"] = "Must be between 0 and 6"

    for field in ["opening_time", "closing_time"]:
        if field in data:
            value = data[field]

            if not isinstance(value, str):
                errors[field] = "Must be a string in HH:MM format"
                continue

            try:
                datetime.strptime(
                    value,
                    "%H:%M",
                )
            except ValueError:
                errors[field] = "Must be in HH:MM format"

    if (
        "opening_time" in data
        and "closing_time" in data
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
            errors["closing_time"] = "Must be later than opening_time"

    return errors
