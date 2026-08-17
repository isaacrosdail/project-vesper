from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.tasks.service import create_tasks_service
from app.shared.decorators import login_plus_session

tasks_bp = Blueprint(
    "tasks", __name__, template_folder="templates", url_prefix="/tasks"
)


@tasks_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    ## TODO(tasks): Overdue rate calc
    overdue_stat = tasks_service.calc_overdue_rate(days=7)
    frog_stat = tasks_service.calc_frog_adherence_rate(days=7)

    ctx = {
        "overdue_stat": overdue_stat,
        "frog_stat": frog_stat,
    }
    return render_template("tasks/dashboard.html", **ctx), 200
