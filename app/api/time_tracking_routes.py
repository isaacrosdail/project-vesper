
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import request, current_app
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.time_tracking.repository import TimeTrackingRepository
from app.modules.time_tracking.service import TimeTrackingService
from app.modules.time_tracking.validators import validate_time_entry
from app.shared.parsers import parse_time_entry_form_data
from app.shared.datetime.helpers import last_n_days_range
from app.shared.decorators import login_plus_session

import logging
logger = logging.getLogger(__name__)

@api_bp.post('/time_tracking/time_entries')
@api_bp.put('/time_tracking/time_entries/<int:entry_id>')
@login_plus_session
def time_entries(session: 'Session', entry_id: int | None = None) -> Any:
        parsed_data = parse_time_entry_form_data(request.form.to_dict())

        typed_data, errors = validate_time_entry(parsed_data)
        if errors:
            logger.info(f"Validation errors: {errors}")
            return validation_failed(errors), 400

        repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
        service = TimeTrackingService(repo, current_user.timezone)
        result = service.save_time_entry(typed_data, entry_id)

        if not result["success"]:
            return api_response(False, result["message"], errors=result["errors"])

        entry = result["data"]["entry"]
        return api_response(
            True,
            result["message"],
            data = entry.to_api_dict()
        ), 201

@api_bp.get("/time_tracking/time_entries/summary")
@login_plus_session
def time_entries_summary(session: 'Session') -> Any:
    last_n_days = int(request.args["lastNDays"])
    repo = TimeTrackingRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(last_n_days, repo.user_tz)
    results = repo.get_all_time_entries_in_window(start_utc, end_utc)

    return api_response(
        True,
        f"Retrieved {len(results)} time entries",
        data = [entry.to_api_dict() for entry in results]
    )