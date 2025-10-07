from flask import jsonify

## Response wrappers

def api_response(
    success: bool, message: str, data: dict = None, errors: dict = None
) -> dict:
    return jsonify(
        {
            "success": success,
            "message": message,
            "data": data or {},
            "errors": errors or {},
        }
    )


def service_response(
    success: bool, message: str, data: dict = None, errors: dict = None
) -> dict:
    return {
        "success": success,
        "message": message,
        "data": data or {},
        "errors": errors or {},
    }


def validation_failed(errors: dict) -> dict:
    return api_response(False, "Validation failed", errors=errors)