
from typing import Any

from flask import Blueprint, render_template

import logging
logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error: Any) -> Any:
    return render_template("errors/404.html"), 404

@errors_bp.app_errorhandler(Exception)
def log_uncaught(e: Exception) -> Any:
    logger.error("Unhandled exception", exc_info=True)
    return render_template("errors/500.html"), 500