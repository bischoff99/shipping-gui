import re
from flask import abort


def validate_customer_input(data):
    # Example: check for required fields and sanitize
    required = ["name", "address", "email"]
    for field in required:
        if field not in data or not isinstance(data[field], str):
            abort(400, description=f"Missing or invalid field: {field}")
    # Basic email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        abort(400, description="Invalid email format")
    # Add more validation as needed
