
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from app._infra.database import database_connection
from app.modules.auth.models import User
from app.modules.auth.repository import create_demo_user, create_owner_user
from app.modules.habits import repository as habits_repo
from app.modules.habits.habit_logic import (calculate_habit_streak,
                                            check_if_completed_today)
from app.modules.habits.models import Habit
from app.modules.metrics import repository as metrics_repo
from app.modules.metrics.models import DailyIntention
from app.modules.tasks import repository as tasks_repo
from app.shared.constants import DEFAULT_LANG
from app.shared.database.operations import delete_all_db_data
from app.shared.database.seed.seed_db import seed_data_for
from app.shared.i18n.messages import msg
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

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
            # TODO: NOTES: Consider extracting into datetime/date helper functions/utils?
            start_of_day_local = datetime.combine(now.date(), time.min, tzinfo=ZoneInfo("Europe/London"))
            start_of_day_utc = start_of_day_local.astimezone(timezone.utc)

            if now.hour < 12:
                greeting = "Good morning"
            elif now.hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"

            # Fetch tasks, habits, today_intention
            tasks = tasks_repo.get_user_tasks(session, current_user.id)
            habits = habits_repo.get_user_habits(session, current_user.id)
            today_intention = metrics_repo.get_user_today_intention(session, current_user.id)
            
            habit_info = {}
            for habit in habits:
                habit_info[habit.id] = {
                    'completed_today': check_if_completed_today(habit.id, current_user.id, session),
                    'streak_count': calculate_habit_streak(habit.id, current_user.id, session)
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
            # Check if daily intention exists for today already
            today_intention = metrics_repo.get_user_today_intention(session, current_user.id)
            
            # If it does, just update the intention field using our fetch data
            if today_intention:
                today_intention.intention = data['intention'] # extract intention key from data
                return jsonify({"success": True, "message": "Successfully created user intention"}), 201
            # Otherwise, we'll add a new entry for DailyIntention
            else:
                new_daily_intention = DailyIntention(
                    intention = data['intention'],
                    user_id = current_user.id
                )
                session.add(new_daily_intention)
                return jsonify({"success": True, "message": "Successfully saved intention"}), 200
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Create & Seed only
@main_bp.route('/init-demo', methods=["POST"])
def init_demo():
    # Boot logged in users first just in case
    try:
        logout_user()
    except Exception:
        pass

    with database_connection() as session:
        # Get or create demo user
        demo_user = session.execute(
            select(User).where(User.username == "guest")
        ).scalar_one_or_none()

        if demo_user is None:
            demo_user = create_demo_user(session)
            session.flush()
            # Seed if we created user
            seed_data_for(session, demo_user)
        else:
            has_data = session.execute(
                select(Habit.id).join(User).where(User.username == "guest").limit(1)
            ).scalar_one_or_none() is not None

            if not has_data:
                seed_data_for(session, demo_user)

        login_user(demo_user) # "quick start": log them in automatically 

    flash(msg("demo_ready", DEFAULT_LANG))
    return redirect(url_for('main.home'))


@main_bp.route('/admin/reset-users', methods=["POST"])
@login_required
def reset_users():
    if current_user.role != 'owner':
        return abort(403)
    
    logout_user()

    # Deletes all data + users, then create fresh demo + admin users
    with database_connection() as session:
        with session.begin(): # Single transaction => should be atomic
            delete_all_db_data(session, include_users=True, reset_sequences=True)
            demo_user = create_demo_user(session)
            seed_data_for(session, demo_user)
            owner_user = create_owner_user(session)
            seed_data_for(session, owner_user)

    flash(msg("db_reset_users", DEFAULT_LANG))
    return redirect(url_for('auth.login'))

# Wipe app data only; reset IDs for more predictable seeding
@main_bp.route('/admin/reset-db', methods=["POST"])
@login_required
def reset_database():
    if current_user.role != 'owner':
        return abort(403)

    # Reset database
    with database_connection() as session:
        with session.begin(): # again, atomic
            delete_all_db_data(session, include_users=False, reset_sequences=True)

    flash(msg("db_reset", DEFAULT_LANG))
    return redirect(url_for('landing_page'))


@main_bp.route('/admin/reset-dev', methods=["POST"])
@login_required
def reset_dev():
    if current_user.role != 'owner':
        return abort(403)
    
    logout_user()

    with database_connection() as session:
        with session.begin():
            delete_all_db_data(session, include_users=True, reset_sequences=True)
            owner_user = create_owner_user(session)
            seed_data_for(session, owner_user)

    flash(msg("db_reset_dev", DEFAULT_LANG))
    return redirect(url_for('main.home'))
