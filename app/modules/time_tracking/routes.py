from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.modules.time_tracking.service import create_time_tracking_service
from app.shared.decorators import login_plus_session

time_tracking_bp = Blueprint(
    "time_tracking", __name__, template_folder="templates", url_prefix="/time_tracking"
)


@time_tracking_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )
    current_date = dth.now_in_timezone(current_user.timezone).date().isoformat()
    ctx = {
        "current_date": current_date,
    }
    return render_template("time_tracking/dashboard.html", **ctx), 200
