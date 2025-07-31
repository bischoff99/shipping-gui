import logging
from logging.handlers import RotatingFileHandler
import os
import sys


def setup_logging(app=None, log_level=None):
    """Setup comprehensive logging for the application"""
    # Set log level based on environment or parameter
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Create logs directory
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Setup formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(name)s [%(pathname)s:%(lineno)d]: %(message)s"
    )
    simple_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    # Setup file handlers
    app_log_file = os.path.join(log_dir, "app.log")
    error_log_file = os.path.join(log_dir, "errors.log")
    api_log_file = os.path.join(log_dir, "api.log")

    # Main application log (rotating)
    app_handler = RotatingFileHandler(
        app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)

    # Error log (rotating, errors only)
    error_handler = RotatingFileHandler(
        error_log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # API log (rotating, for API calls)
    api_handler = RotatingFileHandler(
        api_log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(simple_formatter)

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(simple_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add handlers
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Setup API logger
    api_logger = logging.getLogger("api")
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)

    # Configure Flask app logger if provided
    if app:
        app.logger.handlers.clear()
        app.logger.addHandler(app_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(getattr(logging, log_level))

    # Log startup message
    logging.info("Logging system initialized")
    return logging.getLogger()
