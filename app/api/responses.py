from typing import Any

from flask import Response, jsonify


def api_response(
    *,
    success: bool,
    message: str,
    data: dict[str, Any] | list[dict[str, Any]] | None = None,
) -> Response:
    return jsonify(
        {
            "success": success,
            "message": message,
            "data": data,
        }
    )
