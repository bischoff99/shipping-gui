import logging
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

# Register this in your app factory or main app


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        logger.error(f"HTTPException: {e}", exc_info=True)
        if request.accept_mimetypes.accept_json:
            return jsonify({"error": "An error occurred."}), e.code
        return (
            render_template("error.html", message="An error occurred."),
            e.code,
        )

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        logger.error(f"ValueError: {e}", exc_info=True)
        return jsonify({"error": "Invalid input."}), 400

    @app.errorhandler(KeyError)
    def handle_key_error(e):
        logger.error(f"KeyError: {e}", exc_info=True)
        return jsonify({"error": "Missing data."}), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.critical(f"Unhandled Exception: {e}", exc_info=True)
        return (
            render_template("error.html", message="A server error occurred."),
            500,
        )
