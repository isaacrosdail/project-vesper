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

        now_time = now.strftime("%H:%M:%S")
        now_date = now.strftime("%a, %b %d")

        noon, evening = 12, 18
        greeting = (
            "Good morning"
            if now.hour < noon
            else "Good afternoon"
            if now.hour < evening
            else "Good evening"
        )

        today = dth.now_in_timezone(user_tz).date()  # user's today
        current_date = today.isoformat()  # for time_tracking entry modal's date field

        habits_service = create_habits_service(session, current_user.id, user_tz)
        tasks_service = create_tasks_service(session, current_user.id, user_tz)
        habits = habits_service.habit_repo.get_all()

        start_utc, end_utc = dth.day_range_utc(today, user_tz)
        today_frog = tasks_service.task_repo.get_frog_task_in_window(start_utc, end_utc)
        tasks = tasks_service.task_repo.get_all_regular_tasks()
        filtered_tasks = [
            t
            for t in tasks
            if (t.due_date is None) or dth.is_same_local_date(t.due_date, user_tz)
        ]

        start_utc, end_utc = dth.today_range_utc(user_tz)
        leetcode_records = (
            habits_service.leetcode_repo.get_all_leetcoderecords_in_window(
                start_utc, end_utc
            )
        )

        habit_info = {
            habit.id: {
                "completed_today": habits_service.check_if_completed_today(habit.id),
                "streak_count": habits_service.calculate_habit_streak(habit.id),
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

        ctx = {
            "tasks_progress": tasks_progress,
            "habits_progress": habits_progress,
            "filtered_tasks": filtered_tasks,
            "habits": habits,
            "leetcode_records": leetcode_records,
            "today_frog": today_frog,
            "habit_info": habit_info,
            "now_date": now_date,
            "now_time": now_time,
            "current_date": current_date,
            "greeting": greeting,
            "completions": result
        }
        return render_template("index.html", **ctx), 200


@main_bp.get("/pillars")
def pillars() -> tuple[str, int]:
    """DRAFTING: Pillars mockup to spur ideas"""
    return render_template("DRAFT_pillars.html"), 200

@main_bp.get("/tasks_web")
def tasks_web() -> tuple[str, int]:
    return render_template("tasks_web.html"), 200

@main_bp.get("/health")
def health_check() -> tuple[Response, int]:
    """Return for basic health check / monitoring."""
    status = {"status": "healthy", "timestamp": dth.now_in_timezone("America/Chicago")}
    return jsonify(status), 200
