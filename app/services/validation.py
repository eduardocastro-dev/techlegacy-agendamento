def validate_service_payload(data, partial=False):
    if not isinstance(data, dict):
        return {
            "body": "Request body must be a JSON object"
        }

    errors = {}

    required_fields = [
        "establishment_id",
        "name",
        "duration_minutes",
        "price",
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

    if "name" in data:
        if not isinstance(data["name"], str):
            errors["name"] = "Must be a string"
        elif not data["name"].strip():
            errors["name"] = "Must not be empty"

    if "duration_minutes" in data:
        duration = data["duration_minutes"]

        if not isinstance(duration, int):
            errors["duration_minutes"] = (
                "Must be an integer"
            )
        elif duration <= 0:
            errors["duration_minutes"] = (
                "Must be greater than zero"
            )

    if "price" in data:
        price = data["price"]

        if not isinstance(price, (int, float)):
            errors["price"] = (
                "Must be a number"
            )
        elif price < 0:
            errors["price"] = (
                "Must be greater than or equal to zero"
            )

    return errors