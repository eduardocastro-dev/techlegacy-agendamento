from datetime import datetime


def validate_appointment_payload(data, partial=False):
    if not isinstance(data, dict):
        return {
            "body": "Request body must be a JSON object"
        }

    errors = {}

    required_fields = [
        "establishment_id",
        "service_id",
        "customer_name",
        "customer_phone",
        "starts_at",
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

    if "service_id" in data:
        if not isinstance(data["service_id"], int):
            errors["service_id"] = (
                "Must be an integer"
            )

    if "customer_name" in data:
        if not isinstance(data["customer_name"], str):
            errors["customer_name"] = (
                "Must be a string"
            )
        elif not data["customer_name"].strip():
            errors["customer_name"] = (
                "Must not be empty"
            )

    if "customer_phone" in data:
        if not isinstance(data["customer_phone"], str):
            errors["customer_phone"] = (
                "Must be a string"
            )
        elif not data["customer_phone"].strip():
            errors["customer_phone"] = (
                "Must not be empty"
            )

    if "starts_at" in data:
        value = data["starts_at"]

        if not isinstance(value, str):
            errors["starts_at"] = (
                "Must be in ISO 8601 format"
            )
        else:
            try:
                datetime.fromisoformat(value)
            except ValueError:
                errors["starts_at"] = (
                    "Must be in ISO 8601 format"
                )

    return errors