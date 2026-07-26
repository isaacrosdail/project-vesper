from typing import Any

from flask import Response, jsonify


def success_response(
    *,
    message: str,
    data: dict[str, Any] | list[dict[str, Any]] | None = None,
) -> Response:
    return jsonify(
        {
            "success": True,
            "message": message,
            "data": data,
        }
    )
