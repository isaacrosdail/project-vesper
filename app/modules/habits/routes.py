
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.habits.repository import HabitsRepository
from app.modules.habits.viewmodels import HabitPresenter, HabitViewModel
from app.shared.decorators import login_plus_session
from app.shared.datetime.helpers import last_n_days_range


habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")


@habits_bp.route("/dashboard", methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:
    
    selected_range = request.args.get("range", 7, type=int)

    habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
    start_utc, end_utc = last_n_days_range(selected_range, current_user.timezone)
    habits = habits_repo.get_all_habits_and_tags_in_window(start_utc, end_utc)

    viewmodels = [HabitViewModel(h, current_user.timezone) for h in habits]
    ctx = {
        "selected_range": selected_range,
        "headers": HabitPresenter.build_columns(),
        "habits": viewmodels
    }
    return render_template("habits/dashboard.html", **ctx)
