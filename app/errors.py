import logging
from typing import TypedDict

from flask import Blueprint, render_template
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, NotFound

from app.shared.exceptions import ServiceError


class ErrorResponse(TypedDict):
    success: bool
    code: str
    msg: str
    errors: dict[str, list[str]] | None

def error_response(
    msg: str,
    status_code: int,
    code: str,
    errors: dict[str, list[str]] | None = None
) -> tuple[ErrorResponse, int]:
    return {
        "success": False,
        "code": code,
        "msg": msg,
        "errors": errors,
    }, status_code


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

# Pydantic validation errors
@errors_bp.app_errorhandler(ValidationError)
def handle_validation_error(e: ValidationError) -> tuple[ErrorResponse, int]:
    errors = {}
    for err in e.errors():
        loc = err.get("loc", ())
        field = loc[-1] if loc else "non_field_error"
        errors.setdefault(field, []).append(err["msg"])

    return error_response(
        msg="One or more fields are invalid",
        status_code=400,
        code="VALIDATION_ERROR",
        errors=errors,
    )


@errors_bp.app_errorhandler(ServiceError)
def handle_service_error(e: ServiceError) -> tuple[ErrorResponse, int]:
    return error_response(
        msg=e.message,
        status_code=e.status_code,
        code=e.code,
        errors=e.errors
    )
