from flask import Blueprint, render_template, redirect, url_for
from app.core.database import db_session
from app.modules.tasks import repository as tasks_repo

from app.seed_db import seed_data
from app.core.database import get_engine
from flask import current_app

# Date/Time-related imports
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo

main_bp = Blueprint('main', __name__, template_folder="templates")

@main_bp.route("/", methods=["GET"])
def home():

    # Set reference time once
    now = datetime.now(ZoneInfo("Europe/London"))

    # Today's 00:00 in Europe/London time
    start_of_day_local = datetime.combine(now.date(), time.min, tzinfo=ZoneInfo("Europe/London"))

    # Convert to UTC for DB comparison
    start_of_day_utc = start_of_day_local.astimezone(timezone.utc)
    
    # Get Tasks to pass Anchor Habits to display
    session = db_session()

    # Get all tasks
    tasks = tasks_repo.get_all_tasks(session)
    # List comprehension to filter anchor habits from tasks list
    anchor_habits = [
        task for task in tasks
        if task.type == "habit" and task.is_anchor
    ]

    return render_template(
        "index.html",
        tasks=tasks,
        now=now,
        start_of_day_utc=start_of_day_utc,
        anchor_habits = anchor_habits
    )

@main_bp.route('/reset_db')
def reset_db():
    # TO-DO: Lock this down after adding auth // maybe extract it into a utility function later too
    engine = get_engine(current_app.config) # Current app gives us access to the config within a request context