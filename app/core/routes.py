# Date/Time-related imports
# Conditional import of our seed_dev_db function
import os, sys
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from app.core.database import database_connection, get_engine
from app.modules.habits import repository as habits_repo
from app.modules.habits.habit_logic import (calculate_habit_streak,
                                            check_if_completed_today)
from app.modules.metrics.models import DailyIntention
from app.modules.tasks import repository as tasks_repo
from app.modules.metrics import repository as metrics_repo
from app.common.database.seed.seed_db import seed_db
from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)

from flask_login import current_user

if os.environ.get('APP_ENV') == 'dev':
    try:
        from app.common.database.seed.seed_dev_db import seed_dev_db
        HAS_DEV_TOOLS = True
    except ImportError:
        HAS_DEV_TOOLS = False
else:
    HAS_DEV_TOOLS = False


from app.common.database.operations import delete_all_db_data

main_bp = Blueprint('main', __name__, template_folder="templates")

@main_bp.route("/", methods=["GET"])
def home():

    if not current_user.is_authenticated:
        return render_template('landing_page.html')
    try:
        with database_connection() as session:

            # Calculate time references
            now = datetime.now(ZoneInfo("Europe/London"))
            # Today's 00:00 in Europe/London time
            # TODO: Consider extracting into datetime/date helper functions/utils?
            start_of_day_local = datetime.combine(now.date(), time.min, tzinfo=ZoneInfo("Europe/London"))
            start_of_day_utc = start_of_day_local.astimezone(timezone.utc)

            if now.hour < 12:
                greeting = "Good morning"
            elif now.hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"

            # Fetch tasks, habits, today_intention
            tasks = tasks_repo.get_all_tasks(session)
            habits = habits_repo.get_all_habits(session)
            today_intention = metrics_repo.get_today_intention(session)
            
            habit_info = {}
            for habit in habits:
                habit_info[habit.id] = {
                    'completed_today': check_if_completed_today(habit.id, session),
                    'streak_count': calculate_habit_streak(habit.id, session)
                }

            return render_template(
                "index.html",
                tasks=tasks,
                habits=habits,
                today_intention=today_intention,
                habit_info=habit_info,
                now=now,
                start_of_day_utc=start_of_day_utc,
                greeting=greeting
            )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    
@main_bp.route('/daily-intentions/', methods=["POST"])
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
            # Check if daily intention exists for today already
            today_intention = metrics_repo.get_today_intention(session)
            
            # If it does, just update the intention field using our fetch data
            if today_intention:
                today_intention.intention = data['intention'] # extract intention key from data
                return jsonify({"success": True, "message": "Successfully created user intention"}), 201
            # Otherwise, we'll add a new entry for DailyIntention
            else:
                new_daily_intention = DailyIntention(
                    intention = data['intention']
                )
                session.add(new_daily_intention)
                return jsonify({"success": True, "message": "Successfully saved intention"}), 200
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@main_bp.route('/reset_db', methods=["POST"])
def reset_db():

    # Current app gives us access to the config within a request context
    engine = get_engine(current_app.config)

    # New way with Alembic instead of create_all() -> Delete all DATA but keep all tables
    delete_all_db_data(engine, False)

    seed_db()
    flash('Database has been reset successfully!', 'success')

    return redirect(request.referrer or url_for('index'))

# Wrap in conditional so prod doesn't complain that we don't have a seed_dev_db function/route
if HAS_DEV_TOOLS:
    @main_bp.route('/reset_dev_db', methods=["POST"])
    def reset_dev_db():
        engine = get_engine(current_app.config)
        
        delete_all_db_data(engine, False)
        
        seed_dev_db()
        flash('Dev db reset', 'success')

        return redirect(request.referrer or url_for('index'))