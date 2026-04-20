from __future__ import annotations

from typing import TYPE_CHECKING, get_args

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging

from flask import Response, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import api_response
from app.modules.metrics.models import MetricType
from app.modules.metrics.schemas import DailyMetricsCreate
from app.modules.metrics.service import create_metrics_service
from app.shared.decorators import login_plus_session

logger = logging.getLogger(__name__)


@api_bp.post("/metrics/daily_metrics")
@api_bp.patch("/metrics/daily_metrics/<int:entry_id>")
@login_plus_session
def daily_metrics(session: Session, entry_id: int | None = None) -> tuple[Response, int]:
    validated = DailyMetricsCreate(**request.json)

    metrics_service = create_metrics_service(session, current_user.id, current_user.timezone)
    metrics, is_new = metrics_service.save_daily_metrics(validated, entry_id)
    status_code = 201 if is_new else 200
    message = "created" if is_new else "updated"

    return api_response(
        success=True, message=f"Daily metrics entry {message}", data=metrics.to_api_dict()), status_code



@api_bp.get("/metrics/daily_metrics")
@login_plus_session
def daily_metrics_list(session: Session) -> tuple[Response, int]:
    # VALID_METRIC_TYPES = {"weight", "steps", "calories", "sleep_duration_minutes"}
    metric_type = request.args.get("metric_type")
    if metric_type and metric_type not in get_args(MetricType):
        return api_response(success=False, message="Invalid metric type"), 400
    last_n_days = request.args.get("lastNDays", type=int)
    limit = request.args.get("limit", type=int)

    metrics_service = create_metrics_service(
        session, current_user.id, current_user.timezone
    )

    start_utc, end_utc = None, None
    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
    results = metrics_service.get_daily_metrics(
        start=start_utc, end=end_utc, metric=metric_type, limit=limit
    )

    return api_response(
        success=True,
        message=f"Retrieved {len(results)} entries",
        data=results,
    ), 200


@api_bp.get("/metrics/daily_metrics/aggregate")
@login_plus_session
def daily_metrics_aggregate(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if not last_n_days:
        return api_response(success=False, message="last_n_days missing in query params"), 400
    num_buckets = request.args.get("numBuckets", type=int)
    metrics_service = create_metrics_service(
        session, current_user.id, current_user.timezone
    )

    start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
    if num_buckets:
        data = metrics_service.daily_metrics_repo.get_bucketed_aggregates(start_utc, end_utc, num_buckets)
    else:
        data = metrics_service.daily_metrics_repo.get_aggregates_in_window(start_utc, end_utc)
    if not data:
        return api_response(success=False, message="No matches?"), 404

    return api_response(
        success=True,
        message="Retrieved aggregate",
        data=data,
    ), 200
