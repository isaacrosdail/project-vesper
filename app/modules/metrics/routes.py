from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.modules.metrics.service import create_metrics_service
from app.shared.decorators import login_plus_session

metrics_bp = Blueprint(
    "metrics", __name__, template_folder="templates", url_prefix="/metrics"
)


@metrics_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    daily_metrics_service = create_metrics_service(
        session, current_user.id, current_user.timezone
    )
    metric_entries = daily_metrics_service.daily_metrics_repo.get_all()

    current_date = dth.now_in_timezone(current_user.timezone).date().isoformat()

    ctx = {
        "current_date": current_date,
    }
    return render_template("metrics/dashboard.html", **ctx), 200
