"""
- /health : JSON health check endpoint (for monitoring)
"""

from flask import Blueprint, Response, jsonify, render_template
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app._infra.database import database_connection
from app.modules.habits.service import create_habits_service
from app.modules.tasks.service import create_tasks_service
from app.shared.analytics import create_analytics_service
from app.shared.models import Pillar

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.get("/")
def home() -> tuple[str, int]:
    """
    Return landing page for unauthenticated users,
    homepage for authenticated users.
    """
    if not current_user.is_authenticated:
        return render_template("landing_page.html"), 200

    with database_connection() as session:
        user_tz: str = current_user.timezone
        now = dth.now_in_timezone(user_tz)
        NOON, EVENING = 12, 18
        greeting = (
            "Good morning" if now.hour < NOON
            else "Good afternoon" if now.hour < EVENING
            else "Good evening"
        )
        start_utc, end_utc = dth.today_range_utc(user_tz)

        habits_service = create_habits_service(session, current_user.id, user_tz)
        tasks_service = create_tasks_service(session, current_user.id, user_tz)
        habits = habits_service.habit_repo.get_all()

        today_frog = tasks_service.task_repo.get_frog_task_in_window(start_utc, end_utc)
        tasks = tasks_service.task_repo.get_all_regular_tasks()
        filtered_tasks = [
            t for t in tasks
            if (t.due_datetime is None) or dth.is_same_local_date(t.due_datetime, user_tz)
        ]

        todays_completions = habits_service.completion_repo.get_all_in_window(start_utc, end_utc)
        completed_today_ids = {c.habit_id for c in todays_completions}
        all_streaks = habits_service.get_all_streaks()
        habit_info = {
            habit.id: {
                "completed_today": habit.id in completed_today_ids,
                "streak_count": all_streaks.get(habit.id, 0)
            }
            for habit in habits
        }

        # Progress bars
        habits_progress = habits_service.calculate_all_habits_percentage_this_week()
        tasks_progress = tasks_service.calculate_tasks_progress_today()

        # DEBUG:
        analytics_svc = create_analytics_service(
            session, current_user.id, current_user.timezone
        )
        result = analytics_svc.correlation_method()
        # completions = habits_service.get_daily_completion_counts()

        # TODO: pillars
        pillars = habits_service.pillar_repo.get_all()

        ctx = {
            "tasks_progress": tasks_progress,
            "habits_progress": habits_progress,
            "filtered_tasks": filtered_tasks,
            "habits": habits,
            "today_frog": today_frog,
            "habit_info": habit_info,
            "now": now,
            "greeting": greeting,
            "completions": result,
            "pillars": pillars,
        }
        return render_template("index.html", **ctx), 200


# TODO: clean these up when "finished"
@main_bp.get("/pillars")
def pillars() -> tuple[str, int]:
    """DRAFTING: Pillars mockup to spur ideas"""
    return render_template("DRAFT_pillars.html"), 200

@main_bp.get("/health")
def health_check() -> tuple[Response, int]:
    """Return for basic health check / monitoring."""
    status = {
        "status": "healthy",
        "timestamp": dth.now_utc()
    }
    return jsonify(status), 200
