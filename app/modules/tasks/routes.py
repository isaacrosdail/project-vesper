from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from app.core.database import db_session, db_session

# Import Task model
from app.modules.tasks.models import Task

# Import Task repository
from app.modules.tasks import repository as tasks_repo

# For created_at / completed_at
from datetime import datetime, timezone

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

        return render_template(
            "tasks/dashboard.html",
            task_column_names = task_column_names,
            tasks = tasks)
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
            "is_anchor": bool(request.form.get("is_anchor"))
        }
        # Creating new task Task object
        new_task = Task(
            title=task_data["title"],
            type=task_data["type"],
            is_done=False,
            is_anchor=task_data["is_anchor"],
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

# REMOVE THIS ROUTE? deprecated by update_task route
@tasks_bp.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    session = db_session()
    try:

        # Get corresponding task from db  
        task = session.get(Task, task_id)

        # Update task to be completed, incl. completed_at
        task.is_done = True
        task.completed_at = datetime.now(timezone.utc)
        session.commit()

        return jsonify(success=True)
    finally:
        session.close()

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
        
        db_session.delete(task)
        db_session.commit()
    
        return "", 204     # 204 means No Content (success but nothing to return, used for DELETEs)
    
    finally:
        session.close()