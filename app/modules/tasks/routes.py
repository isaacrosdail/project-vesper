
from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from app._infra.database import database_connection
from app.modules.tasks.models import Task
from app.modules.tasks.repository import TasksRepository
from app.shared.sorting import bubble_sort

tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    try:
        with database_connection() as session:
            # Column names for Task model
            task_headers = Task.build_columns()

            # Fetch tasks, sort
            tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
            tasks = tasks_repo.get_all_tasks()
            bubble_sort(tasks, 'created_at_local', reverse=False)

            ctx = {
                "task_headers": task_headers,
                "tasks": tasks
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