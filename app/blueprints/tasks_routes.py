from flask import Blueprint, render_template, redirect, url_for, request
from app.database import get_session

# Import Task model
from app.modules.tasks.models import Task

# Import Task repository
from app.modules.tasks import repository as tasks_repo

# For created_at / completed_at
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/tasks")
def tasks():

    # Query all tasks
    session = get_session()
    # Column names for Task model
    task_column_names = [
        Task.COLUMN_LABELS.get(col, col)
        for col in Task.__table__.columns.keys()
    ]

    # Fetch Tasks and pass into template
    tasks = tasks_repo.get_all_tasks(session)

    return render_template("tasks/tasks.html",
                           task_column_names = task_column_names,
                           tasks = tasks)

# Create a new task
@tasks_bp.route("/add_task", methods=["GET", "POST"])
def add_task():

    # Process form data and add new task to db
    if request.method == "POST":

        # Parse & sanitize form data
        task_data = {
            "title": request.form.get("title"),
            "type": request.form.get("type"),
            # Value for checkbox is irrelevant
            # If checked, then value is not None, so bool=True (ie, it exists)
            # Otherwise it is None, in which case bool=False 
            "is_anchor": bool(request.form.get("is_anchor"))
        }
        # Creating new task Task object
        new_task = Task(
            title=task_data["title"],
            type=task_data["type"],
            is_done=False,
            is_anchor=task_data["is_anchor"],
            created_at=datetime.now(),
            completed_at=None
        )

        # Add new_task to db
        session = get_session()
        session.add(new_task)
        session.commit()

        return render_template("tasks/tasks.html")
    else:
        return render_template("tasks/add_task.html")
    
@tasks_bp.route("/complete_habit/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    # Get corresponding task from db    
    task = Task.query.get(task_id)

    # Get data from the fetch() request
    data = request.get_json()
    is_checked = data.get("completed", False)