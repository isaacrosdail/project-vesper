# Date/Time-related imports
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

# For reset_db route
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for, jsonify)

from app.core.database import db_session, get_engine
from app.core.db_base import Base
from app.modules.habits import repository as habits_repo
from app.modules.tasks import repository as tasks_repo
from app.seed_db import seed_db
from app.seed_dev_db import seed_dev_db
from app.utils.habit_logic import calculate_habit_streak, check_if_completed_today

from app.modules.habits.models import DailyIntention

main_bp = Blueprint('main', __name__, template_folder="templates")

@main_bp.route("/", methods=["GET"])
def home():

    try:
        # Set reference time once
        now = datetime.now(ZoneInfo("Europe/London"))

        # Today's 00:00 in Europe/London time
        start_of_day_local = datetime.combine(now.date(), time.min, tzinfo=ZoneInfo("Europe/London"))

        # Convert to UTC for DB comparison
        start_of_day_utc = start_of_day_local.astimezone(timezone.utc)
        
        # Get Tasks to pass Anchor Habits to display
        session = db_session()

        # Get all tasks (just regular todos now)
        tasks = tasks_repo.get_all_tasks(session)

        # Get all habits directly from Habit table
        habits = habits_repo.get_all_habits(session)

        # Dict for completed_today status (to move our check out of our template, which caused lazy loading errors)
        completed_today = {}
        for habit in habits:
            completed = check_if_completed_today(habit.id)
            completed_today[habit.id] = completed

        # Get DailyIntention for today, if any
        todayIntention = habits_repo.get_today_intention(session)

        # Get habit streaks
        # Keys of habit.id and values of streak_count
        streaks = {}
        for habit in habits:
            streak_count = calculate_habit_streak(habit.id)
            streaks[habit.id] = streak_count

        return render_template(
            "index.html",
            tasks=tasks,
            now=now,
            start_of_day_utc=start_of_day_utc,
            habits=habits,
            todayIntention=todayIntention,
            streaks=streaks,
            completed_today=completed_today
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

    # See database.py for further comments here, but basically we need to add .remove() here.
    # Otherwise the session may:
    # - Be holding on to ORM mappings that are now invalid
    # - Think certain tables/metadata still exist
    # - Will definitely not be aware of drop_all() happening underneath it
    db_session.remove() # Closes current "converation" the db, but:
    # - other connections might still be open
    # - PostgreSQL won't let you drop tables if anyone is still "talking" to them
    # Since this .remove() didn't fix our issue of hanging/breaking our DB somehow, then the scoped session wasn't the primary cause
    # print("Reset db triggered.")
    # TO-DO: Lock this down after adding auth // maybe extract it into a utility function later too
    engine = get_engine(current_app.config) # Current app gives us access to the config within a request context

    # Drop all tables
    # Tries to delete all tables, but:
    # - If any connection is still using those tables, PostgreSQL will wait
    # - If it waits too long, it looks like your app is frozen/hanging
    Base.metadata.drop_all(bind=engine)

    # Recreate all tables
    Base.metadata.create_all(bind=engine)

    # Re-seed the database with seed_db function
    seed_db()

    # Add confirmation message via flash
    flash('Database has been reset successfully!', 'success')

    return redirect(request.referrer or url_for('index'))

@main_bp.route('/reset_dev_db', methods=["POST"])
def reset_dev_db():
    db_session.remove()
    engine = get_engine(current_app.config)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_dev_db()

    flash('Dev db reset', 'success')
    return redirect(request.referrer or url_for('index'))