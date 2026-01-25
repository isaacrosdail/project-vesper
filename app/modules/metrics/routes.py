from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

import app.shared.datetime.helpers as dth
from app.modules.metrics.service import create_metrics_service
from app.modules.metrics.viewmodels import DailyMetricPresenter, DailyMetricViewModel
from app.shared.collection_utils import sort_by_field
from app.shared.decorators import login_plus_session
from app.shared.parsers_ import get_table_params

metrics_bp = Blueprint(
    "metrics", __name__, template_folder="templates", url_prefix="/metrics"
)


@metrics_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    daily_metrics_service = create_metrics_service(
        session, current_user.id, current_user.timezone
    )

    daily_metrics_params = get_table_params("daily_metrics", "entry_datetime")

    start_utc, end_utc = dth.last_n_days_range(
        daily_metrics_params["range"], current_user.timezone
    )
    metric_entries = (
        daily_metrics_service.daily_metrics_repo.get_all_daily_metrics_in_window(
            start_utc, end_utc
        )
    )
    metric_entries = sort_by_field(
        metric_entries, daily_metrics_params["sort_by"], daily_metrics_params["order"]
    )
    viewmodels = [
        DailyMetricViewModel(e, current_user.timezone) for e in metric_entries
    ]

    today = dth.now_in_timezone(current_user.timezone).date()
    current_date = today.isoformat()

    ctx = {
        "daily_metrics_params": daily_metrics_params,
        "metric_headers": DailyMetricPresenter.build_columns(),
        "metrics": viewmodels,
        "current_date": current_date,
    }
    return render_template("metrics/dashboard.html", **ctx), 200
