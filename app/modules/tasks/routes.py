
from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection, with_db_session
from app.modules.tasks.models import Task, Priority
from app.modules.tasks.repository import TasksRepository
from app.shared.sorting import bubble_sort
from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.modules.tasks.viewmodels import TaskViewModel, TaskPresenter

tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    try:
        with database_connection() as session:

            # Fetch tasks, sort
            tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
            tasks = tasks_repo.get_all_tasks()
            
            viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

            ctx = {
                "task_headers": TaskPresenter.build_columns(),
                "tasks": viewmodel
            }
            return render_template("tasks/dashboard.html", **ctx)
        
    except Exception as e:
        return jsonify({"success": True, "message": str(e)}), 500

# CREATE
@tasks_bp.route("/", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        with database_connection() as session:
            tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
            new_task = tasks_repo.create_task(request.form.get("name"))
            flash("Task added successfully.") # TODO: Standardize to new format
            return jsonify({
                "success": True, 
                "message": "Task added successfully.",
                "task": {
                    "id": new_task.id,
                    "name": new_task.name
                }
            }), 200