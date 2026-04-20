from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.habits.models import LanguageEnum
from app.modules.habits.service import create_habits_service
from app.modules.habits.viewmodels import (
    HabitPresenter,
    HabitViewModel,
    LCRecordPresenter,
    LCRecordViewModel,
)
from app.shared.decorators import login_plus_session
from app.shared.models import Pillar

habits_bp = Blueprint(
    "habits", __name__, template_folder="templates", url_prefix="/habits"
)


@habits_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    habits_service = create_habits_service(
        session, current_user.id, current_user.timezone
    )
    habits = habits_service.habit_repo.get_all_habits_and_tags()
    records = habits_service.leetcode_repo.get_all()
    habits_viewmodels = [HabitViewModel(h, current_user.timezone) for h in habits]
    lcrecords_viewmodels = [
        LCRecordViewModel(r, current_user.timezone) for r in records
    ]

    ## DRAFTING: Habits page's other two cards
    streaks = habits_service.get_all_streaks()
    highest_streak = {"name": "--", "days": "--"}
    lowest_streak = {"name": "--", "days": "--"}
    habit_map = {h.id: h for h in habits}
    if streaks:
        best_id, best_days = max(streaks.items(), key=lambda x: x[1])
        worst_id, worst_days = min(streaks.items(), key=lambda x: x[1])
        # best_habit = next(h for h in habits if h.id == best_id)
        # worst_habit = next(h for h in habits if h.id == worst_id)
        best_habit = habit_map[best_id]
        worst_habit = habit_map[worst_id]
        highest_streak = {"name": best_habit.name, "days": best_days}
        lowest_streak = {"name": worst_habit.name, "days": worst_days}

    # TODO: Pillars
    pillars = session.query(Pillar).filter_by(user_id=current_user.id).all()

    ctx = {
        "habits_headers": HabitPresenter.build_columns(),
        "lcrecords_headers": LCRecordPresenter.build_columns(),
        "habits": habits_viewmodels,
        "lcrecords": lcrecords_viewmodels,
        "languages": LanguageEnum,
        "highest_streak": highest_streak,
        "lowest_streak": lowest_streak,
        "pillars": pillars,
    }
    return render_template("habits/dashboard.html", **ctx), 200
