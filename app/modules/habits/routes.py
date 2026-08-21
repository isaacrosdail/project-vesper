from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template

from app.shared.decorators import login_plus_session

habits_bp = Blueprint(
    "habits", __name__, template_folder="templates", url_prefix="/habits"
)


@habits_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    ctx: dict[str, Any] = {}
    return render_template("habits/dashboard.html", **ctx), 200
