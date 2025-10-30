
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.tasks.repository import TasksRepository
from app.modules.tasks.viewmodels import TaskViewModel, TaskPresenter


tasks_bp = Blueprint('tasks', __name__, template_folder="templates", url_prefix="/tasks")

@tasks_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    tasks_repo = TasksRepository(session, current_user.id, current_user.timezone)
    tasks = tasks_repo.get_all()
    
    viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

    ctx = {
        "task_headers": TaskPresenter.build_columns(),
        "tasks": viewmodel
    }
    return render_template("tasks/dashboard.html", **ctx)
