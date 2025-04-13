from flask import Blueprint, render_template
from app.core.database import get_db_session, db_session
from app.modules.tasks import repository as tasks_repo
# Other imports
from datetime import datetime, timezone

main_bp = Blueprint('main', __name__, template_folder="templates")

@main_bp.route("/")
def home():

    # Display current time on splash screen
    current_time = datetime.now(timezone.utc)
    time_display = current_time.strftime("%H:%M:%S")
    date_display = current_time.strftime("%A, %B %d")
    
    # Enable checking whether completed_at == today
    today = datetime.today()
    
    # Get Tasks to pass Anchor Habits to display
    session = db_session()

    # Get all tasks
    tasks = tasks_repo.get_all_tasks(session)
    # Then filter anchor habits from that
    anchor_habits = [
        task for task in tasks
        if task.type == "habit" and task.is_anchor
    ]

    return render_template("index.html", 
                           time_display=time_display, 
                           date_display=date_display,
                           today=today,
                           anchor_habits = anchor_habits)