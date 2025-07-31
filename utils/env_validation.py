import os
import sys

REQUIRED_ENV_VARS = [
    "SECRET_KEY",
    "DATABASE_URL",
    "VEEQO_API_KEY",
    "EASYSHIP_API_KEY",
    # Add other required variables here
]


def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        sys.stderr.write(
            f"Missing required environment variables: {', '.join(missing)}\n"
        )
        sys.exit(1)
