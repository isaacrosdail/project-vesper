import logging

from flask import Blueprint, render_template
from werkzeug.exceptions import HTTPException, NotFound

logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)

def render_error_page(status_code: int, message: str | None = None) -> tuple[str, int]:
    return render_template("errors/error.html",
                          status_code=status_code,
                          message=message), status_code

@errors_bp.app_errorhandler(400)
def bad_request_error(e: HTTPException) -> tuple[str, int]:
    return render_error_page(400, message=e.description)

@errors_bp.app_errorhandler(403)
def forbidden_error(e: HTTPException) -> tuple[str, int]:
    return render_error_page(403, e.description)

@errors_bp.app_errorhandler(404)
def not_found_error(e: NotFound) -> tuple[str, int]:
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(Exception)
def log_uncaught(e: Exception) -> tuple[str, int]:
    logger.exception("Unhandled exception")
    raise
