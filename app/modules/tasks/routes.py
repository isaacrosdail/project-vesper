# For created_at / completed_at
from datetime import datetime, timezone

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from app.core.database import db_session
from app.utils.sorting import bubble_sort

# Import Task repository
from app.modules.tasks import repository as tasks_repo
# Import Task model
from app.modules.tasks.models import Task

import os

tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/", methods=["GET"])
def dashboard():
    # Fetch Tasks & pass into template
    session = db_session()
    try:
        # Column names for Task model
        task_column_names = [
            Task.COLUMN_LABELS.get(col, col)
            for col in Task.__table__.columns.keys()
        ]

        # Fetch tasks list
        tasks = tasks_repo.get_all_tasks(session)

        # Sort tasks list by most recent Datetime first
        #tasks.sort(key=lambda task: task.created_at, reverse=True)

        # Now using our own bubble sort!
        # Most recently created tasks at bottom of table
        bubble_sort(tasks, 'created_at_local', reverse=False)

        return render_template(
            "tasks/dashboard.html",
            task_column_names = task_column_names,
            tasks = tasks,
            flask_env=os.getenv('FLASK_ENV')
        )
    finally:
        session.close()

# CREATE
@tasks_bp.route("/add", methods=["GET", "POST"])
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
        session = db_session()
        try:
            session.add(new_task)
            session.commit()
            # Display flash() for add confirmation
            flash(f"Task added successfully.")
            return redirect(url_for("tasks.dashboard")) # Redirect after POST - NOT render_template
            # Using redirect here after the form POST follows the best practice of
            # Post/Redirect/Get (PRG) pattern - standard for handling form submissions in web apps
        finally:
            session.close()
    else:
        return render_template("tasks/add_task.html")

# UPDATE
@tasks_bp.route("/<int:task_id>", methods=["PUT", "PATCH"])
def update_task(task_id):
    ## HANDLE CASE WHERE TASK IS NOT FOUND ##
    if request.method == "PATCH":

        session = db_session()
        try:
            task = session.get(Task, task_id) # Grab task by id from db
            data = request.get_json() # Get request body

            if 'title' in data: # If we're updating the title
                task.title = data['title']

                # Save changes & return succes message
                session.commit()
                return jsonify(success=True)

            if 'is_done' in data: # If we're marking task as complete/incomplete
                is_done = data["is_done"]

                # Handle task completion
                task.is_done = is_done
                task.completed_at = (
                    datetime.now(timezone.utc) if is_done else None
                )

                # Save changes to db & return success message
                session.commit()
                return jsonify(success=True)
        finally:
            session.close()
        
    else:
        # POST (will add this later :P)
        pass

# DELETE
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    session = db_session()
    try:
        task = session.get(Task, task_id) # Grab task by id from db

        # If task doesn't exist
        if not task:
            return {"error": "Task not found."}, 404
        
        session.delete(task)
        session.commit()
    
        return "", 204     # 204 means No Content (success but nothing to return, used for DELETEs)
    
    finally:
        session.close()