from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging

from flask import Response, abort, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.time_tracking.service import create_time_tracking_service
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.decorators import login_plus_session
from app.shared.parsers_ import TIME_ENTRY_SCHEMA, parse_form

logger = logging.getLogger(__name__)


@api_bp.post("/time_tracking/time_entries")
@api_bp.put("/time_tracking/time_entries/<int:entry_id>")
@login_plus_session
def time_entries(session: Session, entry_id: int | None = None) -> tuple[Response, int]:
    parsed_data = parse_form(request.form.to_dict(), TIME_ENTRY_SCHEMA)

    typed_data, errors = validate_time_entry(parsed_data)
    if errors:
        logger.info("Validation errors: %s", errors)
        return validation_failed(errors), 400

    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )

    result = time_service.save_time_entry(typed_data, entry_id)
    if not result["success"]:
        return api_response(
            success=False, message=result["message"], errors=result["errors"]
        ), 400

    entry = result["data"]["entry"]
    status_code = 201 if request.method == "POST" else 200

    return api_response(
        success=True, message=result["message"], data=entry.to_api_dict()
    ), status_code


@api_bp.get("/time_tracking/time_entries/summary")
@login_plus_session
def time_entries_summary(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if last_n_days is None:
        abort(400, description="Query parameter 'lastNDays' is required and must be an integer.")

    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )
    start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
    results = time_service.time_entry_repo.get_all_time_entries_in_window(
        start_utc, end_utc
    )

    return api_response(
        success=True,
        message=f"Retrieved {len(results)} time entries",
        data=[entry.to_api_dict() for entry in results],
    ), 200
