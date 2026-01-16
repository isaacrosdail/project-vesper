import logging

from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound

logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(404)
def not_found_error(e: NotFound) -> tuple[str, int]:
    return render_template("errors/404.html"), 404


@errors_bp.app_errorhandler(Exception)
def log_uncaught(e: Exception) -> tuple[str, int]:
    logger.exception("Unhandled exception")
    return render_template("errors/500.html"), 500
