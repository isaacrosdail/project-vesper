
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.habits.repository import HabitsRepository
from app.modules.habits.viewmodels import HabitPresenter, HabitViewModel, LCRecordPresenter, LCRecordViewModel
from app.shared.decorators import login_plus_session
from app.shared.datetime.helpers import last_n_days_range
from app.shared.collections import sort_by_field


habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")


@habits_bp.route("/dashboard", methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:
    
    selected_range = request.args.get("range", 7, type=int)

    records_sort = request.args.get("leet_code_records_sort", "title")
    records_order = request.args.get("leet_code_records_order", "desc")

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(selected_range, current_user.timezone)
    habits = habits_repo.get_all_habits_and_tags()
    records = habits_repo.get_all_leetcoderecords_in_window(start_utc, end_utc)

    records = sort_by_field(records, records_sort, records_order)

    habits_viewmodels = [HabitViewModel(h, current_user.timezone) for h in habits]
    lcrecords_viewmodels = [LCRecordViewModel(r, current_user.timezone) for r in records]
    ctx = {
        "selected_range": selected_range,
        "habits_headers": HabitPresenter.build_columns(),
        "lcrecords_headers": LCRecordPresenter.build_columns(),
        "habits": habits_viewmodels,
        "lcrecords": lcrecords_viewmodels,
        "records_sort": records_sort,
        "records_order": records_order,
    }
    return render_template("habits/dashboard.html", **ctx)
