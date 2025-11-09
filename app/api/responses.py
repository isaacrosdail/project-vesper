
from typing import Any

from flask import jsonify, Response

## Response wrappers

def api_response(
    success: bool,
    message: str,
    data: dict[str, Any] | list[dict[str, Any]] | None = None,
    errors: dict[str, Any] | None = None
) -> Response:
    return jsonify(
        {
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
        }
    )


def service_response(
    success: bool, message: str, data: dict[str, Any] | None = None, errors: dict[str, Any] | None = None
) -> dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
    }


def validation_failed(errors: dict[str, Any]) -> Response:
    return api_response(False, "Validation failed", errors=errors)