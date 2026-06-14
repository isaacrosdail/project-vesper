from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.modules.time_tracking.service import create_time_tracking_service
from app.modules.time_tracking.viewmodels import TimeEntryPresenter, TimeEntryViewModel
from app.shared.decorators import login_plus_session
from app.shared.models import Pillar

time_tracking_bp = Blueprint(
    "time_tracking", __name__, template_folder="templates", url_prefix="/time_tracking"
)


@time_tracking_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    time_service = create_time_tracking_service(
        session, current_user.id, current_user.timezone
    )

    time_entries = time_service.time_entry_repo.get_all()
    viewmodels = [TimeEntryViewModel(e, current_user.timezone) for e in time_entries]

    current_date = dth.now_in_timezone(current_user.timezone).date().isoformat()

    # TODO: for pandas I think?
    # time_entries_debug = time_service.get_time_stuff()

    # TODO: Pillars
    pillars = time_service.pillar_repo.get_all()

    ctx = {
        "entry_headers": TimeEntryPresenter.build_columns(),
        "entries": viewmodels,
        "current_date": current_date,
        "pillars": pillars,
    }
    return render_template("time_tracking/dashboard.html", **ctx), 200
