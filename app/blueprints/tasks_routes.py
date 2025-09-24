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
        }
        # Creating new task Task object
        new_task = Task(
            title=task_data["title"],
            type=task_data["type"],
            is_done=False,
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