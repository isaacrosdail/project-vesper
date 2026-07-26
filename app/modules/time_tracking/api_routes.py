from __future__ import annotations

from typing import TYPE_CHECKING

from app.errors import ErrorResponse, error_response

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging

from flask import Response, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import success_response
from app.modules.time_tracking.schemas import (
    TimeEntryCreate,
    TimeEntryPatch,
    TimeEntryRead,
)
from app.modules.time_tracking.service import create_time_tracking_service
from app.shared.decorators import login_plus_session
from app.shared.exceptions import ServiceError

logger = logging.getLogger(__name__)


@api_bp.post("/time_tracking/time_entries")
@login_plus_session
def post_time_entry(session: Session) -> tuple[Response, int]:
    validated = TimeEntryCreate(**request.json)

    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)
    time_entry = time_service.create_time_entry(validated)
    return success_response(message="Time entry created", data=TimeEntryRead.dump(time_entry)), 201


@api_bp.patch("/time_tracking/time_entries/<int:entry_id>")
@login_plus_session
def patch_time_entry(session: Session, entry_id: int) -> tuple[Response, int]:
    validated = TimeEntryPatch(**request.json)

    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)
    time_entry = time_service.update_time_entry(entry_id, validated)
    return success_response(message="Time entry updated", data=TimeEntryRead.dump(time_entry)), 200


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
    data = [TimeEntryRead.dump(e) for e in results]

    return success_response(message=f"Retrieved {len(results)} time_entries", data=data), 200


@api_bp.get("/time_tracking/time_entries/<int:time_entry_id>")
@login_plus_session
def get_time_entry(session: Session, time_entry_id: int) -> tuple[Response, int]:
    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)
    time_entry = time_service.get_time_entry(time_entry_id)
    return success_response(message="Time entry retrieved", data=TimeEntryRead.dump(time_entry)), 200


@api_bp.delete("/time_tracking/time_entries/<int:time_entry_id>")
@login_plus_session
def delete_time_entry(session: Session, time_entry_id: int) -> tuple[Response, int]:
    time_service = create_time_tracking_service(session, current_user.id, current_user.timezone)
    time_service.delete_time_entry(time_entry_id)
    return success_response(message="Time entry deleted"), 200


@api_bp.get("/time_tracking/time_entries/summary")
@login_plus_session
def time_entries_summary(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if last_n_days is None:
        raise ServiceError("lastNDays is required")

    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )
    start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
    results = time_service.time_entry_repo.get_all_time_entries_in_window(
        start_utc, end_utc
    )

    return success_response(
        message=f"Retrieved {len(results)} time entries",
        data=[TimeEntryRead.dump(entry) for entry in results],
    ), 200

@api_bp.get("/time_tracking/time_entries/aggregate")
@login_plus_session
def time_entries_aggregate(session: Session) -> tuple[Response | ErrorResponse, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if not last_n_days:
        raise ServiceError("lastNDays is required")

    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )
    start_utc, _ = dth.last_n_days_range(last_n_days, current_user.timezone)
    data = time_service.time_entry_repo.get_aggregates_in_window(start_utc)
    if data is None:
        return error_response(message="No matches?", status_code=404, code="NOT_FOUND")

    return success_response(
        message="Retrieved aggregate",
        data=data,
    ), 200
