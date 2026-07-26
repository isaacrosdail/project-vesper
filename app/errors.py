import logging
from typing import Literal, TypedDict

from flask import Blueprint, render_template, request
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException, NotFound

from app.shared.exceptions import ServiceError


class ErrorResponse(TypedDict):
    success: Literal[False]
    code: str
    message: str
    errors: dict[str, list[str]] | None

def error_response(
    message: str,
    status_code: int,
    code: str,
    errors: dict[str, list[str]] | None = None
) -> tuple[ErrorResponse, int]:
    return {
        "success": False,
        "code": code,
        "message": message,
        "errors": errors,
    }, status_code


logger = logging.getLogger(__name__)

errors_bp = Blueprint("errors", __name__)

def is_api_request() -> bool:
    return request.path.startswith("/api")

def render_error_page(status_code: int, title: str, message: str | None = None) -> tuple[str, int]:
    return render_template(
        "errors/error.html",
        status_code=status_code,
        title=title,
        message=message
    ), status_code

@errors_bp.app_errorhandler(404)
def not_found_error(e: NotFound) -> tuple[ErrorResponse | str, int]:
    if is_api_request():
        return error_response(
            message=e.description or e.name,
            status_code=404,
            code=e.name.upper().replace(" ", "_")
        )
    return render_template("errors/404.html"), 404

@errors_bp.app_errorhandler(HTTPException)
def handle_http_exception(e: HTTPException) -> tuple[ErrorResponse | str, int]:
    if is_api_request():
        return error_response(
            message=e.description or e.name,
            status_code=e.code or 500,
            code=e.name.upper().replace(" ", "_")
        )
    return render_error_page(e.code or 500, e.name, e.description or e.name)

# Pydantic validation errors
@errors_bp.app_errorhandler(ValidationError)
def handle_validation_error(e: ValidationError) -> tuple[ErrorResponse, int]:
    errors = {}
    for err in e.errors():
        loc = err.get("loc", ())
        field = loc[-1] if loc else "non_field_error"
        errors.setdefault(field, []).append(err["msg"])
    logger.warning("Validation error on %s: %s (Schema: %s)", request.path, errors, e.title)

    return error_response(
        message="One or more fields are invalid",
        status_code=400,
        code="VALIDATION_ERROR",
        errors=errors,
    )

# Errors raised by services for domain logic
@errors_bp.app_errorhandler(ServiceError)
def handle_service_error(e: ServiceError) -> tuple[ErrorResponse | str, int]:
    if is_api_request():
        return error_response(
            message=e.message,
            status_code=e.status_code,
            code=e.code,
            errors=e.errors
        )
    return render_error_page(e.status_code, "Couldn't complete request", e.message)

@errors_bp.app_errorhandler(Exception)
def log_uncaught(e: Exception) -> tuple[ErrorResponse | str, int]:
    logger.exception("Unhandled exception: %s %s", request.method, request.path)
    if is_api_request():
        return error_response(message="Something went wrong", code="INTERNAL_ERROR", status_code=500)
    return render_error_page(500, "Something went wrong")
