def validate_professional_payload(data, partial=False):
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object"}

    errors = {}
    if not partial and "name" not in data:
        errors["name"] = "This field is required"

    if "name" in data:
        if not isinstance(data["name"], str):
            errors["name"] = "Must be a string"
        elif not data["name"].strip():
            errors["name"] = "Must not be empty"
        elif len(data["name"].strip()) > 120:
            errors["name"] = "Must contain at most 120 characters"

    if "service_ids" in data:
        ids = data["service_ids"]
        if not isinstance(ids, list) or any(
            not isinstance(item, int) or isinstance(item, bool) or item <= 0
            for item in ids
        ):
            errors["service_ids"] = "Must be a list of positive integers"

    if "active" in data and not isinstance(data["active"], bool):
        errors["active"] = "Must be a boolean"

    return errors
