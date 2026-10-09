from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request

from .context import get_current_user


def jwt_required_with_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        user = get_current_user()

        if not user:
            return jsonify({
                "error": "Authenticated user not found"
            }), 401

        return fn(*args, **kwargs)

    return wrapper
