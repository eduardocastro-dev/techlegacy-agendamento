def validate_establishment_update(data):
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object"}

    errors = {}

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str):
            errors["name"] = "Must be a string"

        elif not name.strip():
            errors["name"] = "Must not be empty"

        elif len(name.strip()) > 120:
            errors["name"] = "Must have at most 120 characters"

    if "phone" in data:
        phone = data["phone"]

        if phone is not None and not isinstance(phone, str):
            errors["phone"] = "Must be a string or null"

        elif isinstance(phone, str) and len(phone) > 20:
            errors["phone"] = "Must have at most 20 characters"

    if "slug" in data:
        slug = data["slug"]

        if not isinstance(slug, str):
            errors["slug"] = "Must be a string"

        elif not slug.strip():
            errors["slug"] = "Must not be empty"

        elif len(slug.strip()) > 120:
            errors["slug"] = "Must have at most 120 characters"

        elif " " in slug.strip():
            errors["slug"] = "Must not contain spaces"

    return errors


def validate_account_update(data):
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object"}

    errors = {}

    if "email" in data:
        email = data["email"]

        if not isinstance(email, str):
            errors["email"] = "Must be a string"

        elif not email.strip():
            errors["email"] = "Must not be empty"

        elif len(email.strip()) > 255:
            errors["email"] = "Must have at most 255 characters"

        elif "@" not in email.strip():
            errors["email"] = "Invalid email"

    else:
        errors["email"] = "Email is required"

    return errors


def validate_password_update(data):
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object"}

    errors = {}

    if "current_password" not in data:
        errors["current_password"] = "Current password is required"

    elif not isinstance(data["current_password"], str):
        errors["current_password"] = "Must be a string"

    elif not data["current_password"]:
        errors["current_password"] = "Must not be empty"

    if "new_password" not in data:
        errors["new_password"] = "New password is required"

    elif not isinstance(data["new_password"], str):
        errors["new_password"] = "Must be a string"

    elif len(data["new_password"]) < 6:
        errors["new_password"] = "Must have at least 6 characters"

    if "confirm_password" not in data:
        errors["confirm_password"] = "Password confirmation is required"

    elif not isinstance(data["confirm_password"], str):
        errors["confirm_password"] = "Must be a string"

    elif data.get("new_password") != data["confirm_password"]:
        errors["confirm_password"] = "Passwords do not match"

    return errors
