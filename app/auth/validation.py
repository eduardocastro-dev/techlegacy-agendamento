def validate_register_payload(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    required_fields = [
        "establishment_name",
        "slug",
        "email",
        "password",
    ]

    for field in required_fields:
        if not data.get(field):
            return f"Field '{field}' is required"

    if len(data["password"]) < 6:
        return "Password must contain at least 6 characters"

    return None


def validate_login_payload(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    if not data.get("email"):
        return "Field 'email' is required"

    if not data.get("password"):
        return "Field 'password' is required"

    return None
