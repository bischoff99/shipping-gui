from flask import request, jsonify
from functools import wraps
import os

API_KEYS = [os.getenv("INTERNAL_API_KEY")]  # Set this in your environment


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        if key not in API_KEYS:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated
