from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from zoneinfo import ZoneInfo

from flask import request, Response
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.metrics.repository import DailyMetricsRepository
from app.modules.metrics.service import create_metrics_service
from app.modules.metrics.validators import validate_daily_entry
from app.shared.parsers import parse_daily_entry_form_data
from app.shared.datetime.helpers import last_n_days_range
from app.shared.decorators import login_plus_session


import logging
logger = logging.getLogger(__name__)

@api_bp.post("/metrics/daily_metrics")
@api_bp.put("/metrics/daily_metrics/<int:entry_id>")
@login_plus_session
def daily_metrics(session: 'Session', entry_id: int | None = None) -> tuple[Response, int]:
    parsed_data = parse_daily_entry_form_data(request.form.to_dict())
    typed_data, errors = validate_daily_entry(parsed_data)
    if errors:
        return validation_failed(errors), 400

    metrics_service = create_metrics_service(session, current_user.id, current_user.timezone)
    result = metrics_service.save_daily_metrics(typed_data, entry_id)

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"]), 400

    entry = result["data"]["entry"]
    return api_response(
        True,
        result["message"],
        data = entry.to_api_dict()
    ), 201


@api_bp.get("/metrics/daily_metrics/timeseries")
@login_plus_session
def daily_metrics_timeseries(session: 'Session') -> tuple[Response, int]:
    metric_type = request.args["metric_type"]
    last_n_days = request.args.get("lastNDays", 7, type=int)

    start_utc, end_utc = last_n_days_range(last_n_days, current_user.timezone)
    metrics_service = create_metrics_service(session, current_user.id, current_user.timezone)
    results = metrics_service.daily_metrics_repo.get_daily_metrics_by_type_in_window(metric_type, start_utc, end_utc)

    logger.debug(f"result: {results}")
    return api_response(
        True,
        f"Retrieved {len(results)} {metric_type} entries",
        data = [
            {
                "date": dt.astimezone(ZoneInfo(current_user.timezone)).isoformat(),
                "value": value
            }
            for dt, value in results
        ]
    ), 200

@api_bp.get("/metrics/daily_metrics")
@login_plus_session
def daily_metrics_list(session: 'Session') -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", 7, type=int)

    metrics_service = create_metrics_service(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(last_n_days, current_user.timezone)
    result = metrics_service.daily_metrics_repo.get_all_daily_metrics_in_window(start_utc, end_utc)

    logger.debug(f"result: {result}")
    return api_response(
        True,
        f"Retrieved {len(result)} entries",
        data = [entry.to_api_dict() for entry in result]
    ), 201