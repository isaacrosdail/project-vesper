
from flask import Blueprint, render_template
from flask_login import current_user

from app._infra.database import database_connection
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import (calculate_habit_streak,
                                        check_if_completed_today)
from app.modules.tasks.repository import TasksRepository
from app.shared.datetime.helpers import convert_to_timezone, today_range

main_bp = Blueprint('main', __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def home():

    if not current_user.is_authenticated:
        return render_template('landing_page.html')

    with database_connection() as session:
        now = convert_to_timezone(current_user.timezone)
        now_time = now.strftime("%H:%M:%S")
        now_date = now.strftime("%A, %B %d")

        if now.hour < 12:
            greeting = "Good morning"
        elif now.hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # Fetch tasks, habits
        habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
        tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
        habits = habits_repo.get_all_habits()
        today_frog = tasks_repo.get_today_frog()
        tasks = tasks_repo.get_all_regular_tasks()

        # Get today's leetcode records
        start_utc, end_utc = today_range(current_user.timezone)
        leetcode_records = habits_repo.get_all_leetcoderecords_in_window(start_utc, end_utc)
        
        habit_info = {}
        for habit in habits:
            habit_info[habit.id] = {
                'completed_today': check_if_completed_today(session, current_user.id, habit.id, current_user.timezone),
                'streak_count': calculate_habit_streak(session, current_user.id, habit.id, current_user.timezone)
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
