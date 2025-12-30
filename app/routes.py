"""
- /health : JSON health check endpoint (for monitoring)
"""
from typing import Any

from flask import Blueprint, render_template, jsonify
from flask_login import current_user


from app._infra.database import database_connection
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.service import TasksService
from app.shared.datetime.helpers import (
    today_range_utc,
    day_range_utc,
    now_in_timezone,
    is_same_local_date,
)

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.get("/")
def home() -> Any:
    """Return landing page for unauthenticated users, homepage for authenticated users."""
    if not current_user.is_authenticated:
        return render_template("landing_page.html")

    with database_connection() as session:
        user_tz_str: str = current_user.timezone
        now = now_in_timezone(user_tz_str)

        now_time = now.strftime("%H:%M:%S")
        now_date = now.strftime("%a, %b %d")
        greeting = (
            "Good morning" if now.hour < 12
            else "Good afternoon" if now.hour < 18
            else "Good evening"
        )

        today = now_in_timezone(user_tz_str).date()  # user's today
        current_date = today.isoformat()  # for time_tracking entry modal's date field

        # Fetch tasks, habits
        habits_repo = HabitsRepository(session, current_user.id, user_tz_str)
        tasks_repo = TasksRepository(session, current_user.id, user_tz_str)
        habits = habits_repo.get_all()

        start_utc, end_utc = day_range_utc(today, user_tz_str)  # UTC bounds
        today_frog = tasks_repo.get_frog_task_in_window(start_utc, end_utc)
        tasks = tasks_repo.get_all_regular_tasks()
        filtered_tasks = [
            t for t in tasks
            if (t.due_date is None) or is_same_local_date(t.due_date, user_tz_str)
        ]


        start_utc, end_utc = today_range_utc(user_tz_str)
        leetcode_records = habits_repo.get_all_leetcoderecords_in_window(
            start_utc, end_utc
        )

        habits_service = HabitsService(habits_repo, user_tz_str)
        habit_info = {
            habit.id: {
                "completed_today": habits_service.check_if_completed_today(habit.id),
                "streak_count": habits_service.calculate_habit_streak(habit.id),
            }
            for habit in habits
        }

        # Progress bars
        habits_progress = habits_service.calculate_all_habits_percentage_this_week()
        tasks_svc = TasksService(tasks_repo, user_tz_str)
        tasks_progress = tasks_svc.calculate_tasks_progress_today()

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
        }
        return render_template("index.html", **ctx)


@main_bp.get("/health")
def health_check() -> Any:
    """Return for basic health check / monitoring."""
    status = {"status": "healthy", "timestamp": now_in_timezone("America/Chicago")}
    return jsonify(status)
