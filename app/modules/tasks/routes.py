from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.tasks.service import create_tasks_service
from app.modules.tasks.viewmodels import TaskPresenter, TaskViewModel
from app.shared.decorators import login_plus_session
from app.shared.models import Pillar

tasks_bp = Blueprint(
    "tasks", __name__, template_folder="templates", url_prefix="/tasks"
)


@tasks_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    # TODO: Since we access pillar.name, check to ensure we eager-load pillars
    # selectinload(Task.pillars) in repo method
    tasks = tasks_service.task_repo.get_all()

    viewmodel = [TaskViewModel(t, current_user.timezone) for t in tasks]

    ## WIP: Overdue rate calc
    overdue_stat = tasks_service.calc_overdue_rate(days=7)
    frog_stat = tasks_service.calc_frog_adherence_rate(days=7)

    # TODO: Pillars
    pillars = tasks_service.pillar_repo.get_all()

    # TODO: Test
    tasks_service.task_repo.get_max_sort_key()


    ctx = {
        "task_headers": TaskPresenter.build_columns(),
        "tasks": viewmodel,
        "tasks_raw": tasks,
        "overdue_stat": overdue_stat,
        "frog_stat": frog_stat,
        "pillars": pillars,
    }
    return render_template("tasks/dashboard.html", **ctx), 200
