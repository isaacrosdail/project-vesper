from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.habits.service import create_habits_service
from app.modules.habits.viewmodels import (
    HabitPresenter,
    HabitViewModel,
    LCRecordPresenter,
    LCRecordViewModel,
)
from app.shared.collection_utils import sort_by_field
from app.shared.datetime.helpers import last_n_days_range
from app.shared.decorators import login_plus_session
from app.shared.parsers_ import get_table_params

habits_bp = Blueprint(
    "habits", __name__, template_folder="templates", url_prefix="/habits"
)


@habits_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    records_params = get_table_params("leet_code_records", "created_at")

    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    start_utc, end_utc = last_n_days_range(
        records_params["range"], current_user.timezone
    )
    habits = habits_service.habit_repo.get_all_habits_and_tags()
    records = habits_service.leetcode_repo.get_all_leetcoderecords_in_window(
        start_utc, end_utc
    )

    records = sort_by_field(records, records_params["sort_by"], records_params["order"])

    habits_viewmodels = [HabitViewModel(h, current_user.timezone) for h in habits]
    lcrecords_viewmodels = [
        LCRecordViewModel(r, current_user.timezone) for r in records
    ]
    ctx = {
        "records_params": records_params,
        "habits_headers": HabitPresenter.build_columns(),
        "lcrecords_headers": LCRecordPresenter.build_columns(),
        "habits": habits_viewmodels,
        "lcrecords": lcrecords_viewmodels,
    }
    return render_template("habits/dashboard.html", **ctx), 200
