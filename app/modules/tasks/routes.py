# For created_at / completed_at
from datetime import datetime, timezone

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from app.core.database import db_session, database_connection
from app.utils.sorting import bubble_sort

# Import Task repository
from app.modules.tasks import repository as tasks_repo
# Import Task model
from app.modules.tasks.models import Task

import os

tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/dashboard", methods=["GET"])
def dashboard():

    try:
        with database_connection() as session:
            # Column names for Task model
            task_column_names = [
                Task.COLUMN_LABELS.get(col, col)
                for col in Task.__table__.columns.keys()
            ]

            # Fetch tasks, sort
            tasks = tasks_repo.get_all_tasks(session)
            bubble_sort(tasks, 'created_at_local', reverse=False)

            return render_template(
                "tasks/dashboard.html",
                task_column_names = task_column_names,
                tasks = tasks
            )
        
    except Exception as e:
        return jsonify({"success": True, "message": str(e)}), 500

# CREATE
@tasks_bp.route("/", methods=["GET", "POST"])
def tasks():

    # Process form data and add new task to db
    if request.method == "POST":

        # Parse & sanitize form data
        task_data = {
            "title": request.form.get("title"),
            "type": request.form.get("type"),
            # Value for checkbox is irrelevant
            # If checked, then value is not None, so bool=True (ie, it exists)
            # Otherwise it is None, in which case bool=False 
            #"is_anchor": bool(request.form.get("is_anchor"))
        }
        # Creating new task Task object
        new_task = Task(
            title=task_data["title"],
            type=task_data["type"],
            is_done=False,
            created_at=datetime.now(timezone.utc),
            completed_at=None
        )

        # Add new_task to db
        with database_connection() as session:
            session.add(new_task)
            flash(f"Task added successfully.")
            return redirect(url_for("tasks.dashboard")) # Redirect after POST - NOT render_template
            # Using redirect here after the form POST follows the best practice of
            # Post/Redirect/Get (PRG) pattern - standard for handling form submissions in web apps
            
    # GET => Return add_task form page
    else:
        return render_template("tasks/add_task.html")
