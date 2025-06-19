# Date/Time-related imports
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

# For reset_db route
from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from sqlalchemy import text

from app.core.database import db_session, get_engine
from app.core.db_base import Base
from app.modules.habits import repository as habits_repo
from app.modules.habits.habit_logic import (calculate_habit_streak,
                                            check_if_completed_today)
from app.modules.habits.models import DailyIntention
from app.modules.tasks import repository as tasks_repo
from app.seed_db import seed_db

# Conditional import of our seed_dev_db function
import os
if os.environ.get('APP_ENV') == 'dev':
    try:
        from app.seed_dev_db import seed_dev_db
        HAS_DEV_TOOLS = True
    except ImportError:
        HAS_DEV_TOOLS = False
else:
    HAS_DEV_TOOLS = False


from app.utils.db_utils import delete_all_db_data

main_bp = Blueprint('main', __name__, template_folder="templates")

@main_bp.route("/", methods=["GET"])
def home():

    session = db_session()
    try:
        # Calculate time references
        now = datetime.now(ZoneInfo("Europe/London"))
        # Today's 00:00 in Europe/London time
        start_of_day_local = datetime.combine(now.date(), time.min, tzinfo=ZoneInfo("Europe/London"))
        start_of_day_utc = start_of_day_local.astimezone(timezone.utc)

        # Fetch tasks, habits, today_intention, dailymetric
        tasks = tasks_repo.get_all_tasks(session)
        habits = habits_repo.get_all_habits(session)
        todayIntention = habits_repo.get_today_intention(session)

        # Dict for completed_today status (to move our check out of our template, which caused lazy loading errors)
        completed_today = {}
        for habit in habits:
            completed = check_if_completed_today(habit.id)
            completed_today[habit.id] = completed
        # Get habit streaks
        # Keys of habit.id and values of streak_count
        streaks = {}
        for habit in habits:
            streak_count = calculate_habit_streak(habit.id)
            streaks[habit.id] = streak_count

        return render_template(
            "index.html",
            tasks=tasks,
            habits=habits,
            todayIntention=todayIntention,
            completed_today=completed_today,
            streaks=streaks,
            now=now,
            start_of_day_utc=start_of_day_utc
        )
    finally:
        session.close()

@main_bp.route('/daily-intentions/', methods=["POST"])
def update_daily_intention():
    try:
        # Get json data from fetch request
        data = request.get_json()
        # Check if daily intention exists for today already
        session = db_session()
        todayIntention = habits_repo.get_today_intention(session)

        # If it does, just update the intention field using our fetch data
        if todayIntention:
            todayIntention.intention = data['intention'] # extract intention key from data
        # Otherwise, we'll add a new entry for DailyIntention
        else:
            new_daily_intention = DailyIntention(
                intention = data['intention']
            )
            session.add(new_daily_intention)
        session.commit()
        
        # Return statement for json success
        return jsonify({'status': 'success'})
    except Exception as e:
        # Undo changes if something failed
        session.rollback()
        # Return statement for error
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        session.close()

@main_bp.route('/reset_db', methods=["POST"])
def reset_db():

    # Current app gives us access to the config within a request context
    engine = get_engine(current_app.config)

    # New way with Alembic instead of create_all() -> Delete all DATA but keep all tables
    delete_all_db_data(engine, False)

    # Re-seed the database with seed_db function & confirm flash()
    seed_db()
    flash('Database has been reset successfully!', 'success')

    return redirect(request.referrer or url_for('index'))

# Wrap in conditional so prod doesn't complain that we don't have a seed_dev_db function/route
if HAS_DEV_TOOLS:
    @main_bp.route('/reset_dev_db', methods=["POST"])
    def reset_dev_db():

        engine = get_engine(current_app.config)
        
        # New way with Alembic instead of create_all()
        delete_all_db_data(engine, False)   # Using util function in db_utils.py
        
        # Re-seed & confirm flash()
        seed_dev_db()
        flash('Dev db reset', 'success')

        return redirect(request.referrer or url_for('index'))