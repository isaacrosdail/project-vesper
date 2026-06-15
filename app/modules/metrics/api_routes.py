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
from app.modules.auth.models import UnitSystemEnum
from app.modules.metrics.models import MetricType
from app.modules.metrics.schemas import DailyMetricsCreate
from app.modules.metrics.service import create_metrics_service
from app.shared.decorators import login_plus_session
from app.shared.exceptions import ServiceError
from app.shared.utils import kg_to_lbs

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
    metric_type = request.args.get("metric_type")
    if metric_type and metric_type not in get_args(MetricType):
        raise ServiceError("Invalid metric type")
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


@api_bp.get("/metrics/daily_metrics/<int:entry_id>")
@login_plus_session
def get_daily_metrics_entry(session: Session, entry_id: int) -> tuple[Response, int]:
    metrics_service = create_metrics_service(session, current_user.id, current_user.timezone)
    entry = metrics_service.get_daily_metrics_entry(entry_id)
    data = entry.to_api_dict()

    if data.get("weight") is not None and current_user.units is UnitSystemEnum.IMPERIAL:
        data["weight"] = kg_to_lbs(data["weight"])
        data["weight_units"] = "lbs"
    elif "weight" in data:
        data["weight_units"] = "kg"

    return api_response(success=True, message="Daily metrics retrieved", data=data), 200


@api_bp.delete("/metrics/daily_metrics/<int:daily_metrics_id>")
@login_plus_session
def delete_daily_metrics(session: Session, daily_metrics_id: int) -> tuple[Response, int]:
    metrics_service = create_metrics_service(session, current_user.id, current_user.timezone)
    metrics_service.delete_daily_metrics(daily_metrics_id)
    return api_response(success=True, message="Daily metrics entry deleted"), 200


@api_bp.get("/metrics/daily_metrics/aggregate")
@login_plus_session
def daily_metrics_aggregate(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    if not last_n_days:
        raise ServiceError("lastNDays is required")
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
        return api_response(success=True, message="No data for this window", data=[]), 200
    return api_response(success=True, message=f"Retrieved {len(data)} buckets", data=data), 200
