
from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection
from app.modules.habits.repository import HabitsRepository
from app.modules.habits.service import (calculate_habit_streak,
                                        check_if_completed_today)
from app.modules.metrics.repository import DailyMetricsRepository
from app.shared.datetime.helpers import datetime_local, today_range

main_bp = Blueprint('main', __name__, template_folder="templates")


@main_bp.route("/", methods=["GET"])
def home():

    if not current_user.is_authenticated:
        return render_template('landing_page.html')
    try:
        with database_connection() as session:
            now = datetime_local(current_user.timezone)
            now_date = now.strftime("%H:%M:%S")
            now_time = now.strftime("%A, %B %d")

            if now.hour < 12:
                greeting = "Good morning"
            elif now.hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"

            # Fetch tasks, habits, today_intention
            start_utc, end_utc = today_range(current_user.timezone)
            habits_repo = HabitsRepository(session, current_user.id, current_user.timezone)
            metrics_repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
            habits = habits_repo.get_all_habits()
            today_intention = metrics_repo.get_intention_for_day(start_utc, end_utc)
            
            habit_info = {}
            for habit in habits:
                habit_info[habit.id] = {
                    'completed_today': check_if_completed_today(session, current_user.id, habit.id, current_user.timezone),
                    'streak_count': calculate_habit_streak(session, current_user.id, habit.id, current_user.timezone)
                }

            ### Each key becomes its own top-level var in template (No 'ctx.' prefix required)
            ctx = {
                #"tasks": tasks,
                "habits": habits,
                "today_intention": today_intention,
                "habit_info": habit_info,
                "now": now,
                "now_date": now_date,
                "now_time": now_time,
                "greeting": greeting
            }
            return render_template("index.html", **ctx)
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    
@main_bp.route('/daily-intentions/', methods=["POST"])
@login_required
def update_daily_intention():
    try:
        # Get JSON data from request body & parse into Python dict
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "Error: data is None"}), 400
        
        intention = data.get('intention')
        if not intention:
            return jsonify({"success": False, "message": "No intention provided."}), 400

        with database_connection() as session:
            start_utc, end_utc = today_range(current_user.timezone)
            metrics_repo = DailyMetricsRepository(session, current_user.id, current_user.timezone)
            today_intention = metrics_repo.get_intention_for_day(start_utc, end_utc)

            if today_intention:
                today_intention.intention = data['intention']
                return jsonify({"success": True, "message": "Successfully created user intention"}), 201
            else:
                new_daily_intention = metrics_repo.create_daily_intention(data['intention'])
                return jsonify({"success": True, "message": "Successfully saved intention"}), 200
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
