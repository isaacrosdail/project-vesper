"""
- /health : JSON health check endpoint (for monitoring)
"""

from flask import Blueprint, render_template, jsonify
from flask_login import current_user

from app.shared.constants import DEFAULT_HEALTH_TIMEZONE
from app._infra.database import database_connection
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import HabitsService
from app.modules.tasks.repository import TasksRepository
from app.shared.datetime.helpers import convert_to_timezone, today_range_utc, day_range_utc, now_in_timezone

main_bp = Blueprint('main', __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def home():

    if not current_user.is_authenticated:
        return render_template('landing_page.html')

    with database_connection() as session:
        now = now_in_timezone(current_user.timezone)
        now_time = now.strftime("%H:%M:%S")
        now_date = now.strftime("%A, %B %d")

        if now.hour < 12:
            greeting = "Good morning"
        elif now.hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        today = now_in_timezone(current_user.timezone).date() # user's today
        start_utc, end_utc = day_range_utc(today, current_user.timezone) # UTC bounds

        # Fetch tasks, habits
        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
        habits = habits_repo.get_all_habits()
        today_frog = tasks_repo.get_frog_task_in_window(start_utc, end_utc)
        tasks = tasks_repo.get_all_regular_tasks()

        # Get today's leetcode records
        start_utc, end_utc = today_range_utc(current_user.timezone)
        leetcode_records = habits_repo.get_all_leetcoderecords_in_window(start_utc, end_utc)
        
        habits_service = HabitsService(habits_repo, current_user.timezone)
        habit_info = {}
        for habit in habits:
            habit_info[habit.id] = {
                'completed_today': habits_service.check_if_completed_today(habit.id),
                'streak_count': habits_service.calculate_habit_streak(habit.id)
            }

        ### Each key becomes its own top-level var in template (No 'ctx.' prefix required)
        ctx = {
            "tasks": tasks,
            "habits": habits,
            "today_frog": today_frog,
            "habit_info": habit_info,
            "now": now,
            "now_date": now_date,
            "now_time": now_time,
            "greeting": greeting,
            "leetcode_records": leetcode_records
        }
        return render_template("index.html", **ctx)

@main_bp.route('/health')
def health_check():
    """Basic health check for monitoring."""
    status = {
        'status': 'healthy',
        'timestamp': now_in_timezone(DEFAULT_HEALTH_TIMEZONE)
    }
    return jsonify(status)