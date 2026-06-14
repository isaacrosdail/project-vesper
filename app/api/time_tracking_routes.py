from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging

from flask import Response, abort, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import api_response
from app.modules.time_tracking.schemas import TimeEntryCreate, TimeEntryPatch
from app.modules.time_tracking.service import create_time_tracking_service
from app.shared.decorators import login_plus_session

logger = logging.getLogger(__name__)


@api_bp.post("/time_tracking/time_entries")
@login_plus_session
def post_time_entry(session: Session) -> tuple[Response, int]:
    validated = TimeEntryCreate(**request.json)

    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)
    time_entry = time_service.create_time_entry(validated)
    return api_response(success=True, message="Time entry created", data=time_entry.to_api_dict()), 201


@api_bp.patch("/time_tracking/time_entries/<int:entry_id>")
@login_plus_session
def patch_time_entry(session: Session, entry_id: int) -> tuple[Response, int]:
    validated = TimeEntryPatch(**request.json)

    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)
    time_entry = time_service.update_time_entry(entry_id, validated)
    return api_response(success=True, message="Time entry updated", data=time_entry.to_api_dict()), 200


@api_bp.get("/time_tracking/time_entries")
@login_plus_session
def time_entries_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)

    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = time_service.time_entry_repo.get_all_time_entries_in_window(start_utc, end_utc)
    else:
        results = time_service.time_entry_repo.get_all()
    data = [t.to_api_dict() for t in results]

    return api_response(success=True, message=f"Retrieved {len(results)} time_entries", data=data), 200


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

@api_bp.get("/time_tracking/time_entries/aggregate")
@login_plus_session
def time_entries_aggregate(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if not last_n_days:
        return api_response(success=False, message="last_n_days missing in query params"), 400

    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )
    start_utc, _ = dth.last_n_days_range(last_n_days, current_user.timezone)
    data = time_service.time_entry_repo.get_aggregates_in_window(start_utc)
    if data is None:
        return api_response(success=False, message="No matches?"), 404

    return api_response(
        success=True,
        message="Retrieved aggregate",
        data=data,
    ), 200
