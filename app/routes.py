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
from app.shared.datetime.helpers import today_range_utc, day_range_utc, now_in_timezone, is_same_local_date

main_bp = Blueprint('main', __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def home() -> Any:

    if not current_user.is_authenticated:
        return render_template('landing_page.html')

    with database_connection() as session:
        now = now_in_timezone(current_user.timezone)
        now_time = now.strftime("%H:%M:%S")
        now_date = now.strftime("%a, %b %d")

        if now.hour < 12:
            greeting = "Good morning"
        elif now.hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        today = now_in_timezone(current_user.timezone).date() # user's today
        current_date = today.isoformat() # for time_tracking entry modal's date field
        start_utc, end_utc = day_range_utc(today, current_user.timezone) # UTC bounds

        # Fetch tasks, habits
        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
        habits = habits_repo.get_all()
        today_frog = tasks_repo.get_frog_task_in_window(start_utc, end_utc)
        tasks = tasks_repo.get_all_regular_tasks()
        filtered_tasks =[
            t
            for t in tasks
            if (t.due_date is None) or is_same_local_date(t.due_date, current_user.timezone)
        ]
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

        ###### WIP - For habit completion this week 'feature'
        habits_progress = habits_service.calculate_all_habits_percentage_this_week()

        ## FOR TASKS progress bar/count
        tasks_svc = TasksService(tasks_repo, current_user.timezone)
        tasks_progress = tasks_svc.calculate_tasks_progress_today()
        ######

        ### Each key becomes its own top-level var in template (No 'ctx.' prefix required)
        ctx = {
            'tasks_progress': tasks_progress,
            'habits_progress': habits_progress,
            "filtered_tasks": filtered_tasks,
            "habits": habits,
            "today_frog": today_frog,
            "habit_info": habit_info,
            "now": now,
            "now_date": now_date,
            "now_time": now_time,
            "greeting": greeting,
            "leetcode_records": leetcode_records,
            "current_date": current_date,
        }
        return render_template("index.html", **ctx)

@main_bp.route('/health')
def health_check() -> Any:
    """Basic health check for monitoring."""
    status = {
        'status': 'healthy',
        'timestamp': now_in_timezone("America/Chicago")
    }
    return jsonify(status)