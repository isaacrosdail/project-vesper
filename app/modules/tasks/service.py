from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.auth.models import User

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import app.shared.datetime.helpers as dth
from app.api.responses import service_response
from app.modules.tasks.repository import TaskRepository
from app.shared.hooks import register_patch_hook


class TasksService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        task_repo: TaskRepository,
    ) -> None:
        self.session = session
        self.task_repo = task_repo
        self.user_tz = user_tz

    def save_task(
        self, typed_data: dict[str, Any], task_id: int | None
    ) -> dict[str, Any]:
        # Attach due_date datetime
        typed_data["due_date"] = self.to_eod_datetime(
            typed_data.get("due_date"), self.user_tz
        )

        # Check for existing frog task
        if typed_data["is_frog"]:
            start_utc, end_utc = dth.day_range_utc(
                typed_data["due_date"].date(), self.user_tz
            )

            existing_frog = self.task_repo.get_frog_task_in_window(start_utc, end_utc)
            if existing_frog:
                frog_date = typed_data["due_date"].date().isoformat()
                return service_response(
                    success=False,
                    message="Error: Duplicate frog task",
                    errors={
                        "frog_task": [f"You already have a 'frog' task for {frog_date}"]
                    },
                )

        ### UPDATE
        if task_id:
            task = self.task_repo.get_by_id(task_id)
            if not task:
                return service_response(success=False, message="Task not found")

            for field, value in typed_data.items():
                setattr(task, field, value)

            return service_response(
                success=True, message="Task updated", data={"task": task}
            )
        # CREATE
        else:
            task = self.task_repo.create_task(
                name=typed_data["name"],
                priority=typed_data.get("priority"),
                due_date=typed_data.get("due_date"),
                is_frog=typed_data["is_frog"],
            )
            return service_response(
                success=True, message="Task added", data={"task": task}
            )

    def to_eod_datetime(self, date: date | None, tz_str: str) -> datetime | None:
        """Convert a date to exclusive EOD datetime in given timezone."""
        if not date:
            return None
        tz = ZoneInfo(tz_str)
        start_of_day = datetime.combine(date, time.min, tzinfo=tz)
        eod_midnight = start_of_day + timedelta(days=1)
        return eod_midnight - timedelta(seconds=1)

    def calculate_tasks_progress_today(self) -> dict[str, Any]:
        all_tasks = self.task_repo.get_all()

        # Count completed vs expected for today
        num_completed = 0
        num_expected = 0

        for task in all_tasks:
            due_today = task.due_date and dth.is_same_local_date(
                task.due_date, self.user_tz
            )
            completed_today = task.completed_at and dth.is_same_local_date(
                task.completed_at, self.user_tz
            )

            if due_today:
                num_expected += 1
                if completed_today:
                    num_completed += 1

            elif completed_today and task.due_date is None:
                # "spontaneous" task, completed today without a due date
                num_completed += 1
                num_expected += 1

        percent_complete = (
            (num_completed / num_expected * 100) if num_expected > 0 else 0
        )

        return {
            "completed": num_completed,
            "total": num_expected,
            "percent": percent_complete,
        }


def create_tasks_service(session: Session, user_id: int, user_tz: str) -> TasksService:
    """Factory function to instantiate HabitsService with required repositories."""
    return TasksService(
        session=session,
        user_tz=user_tz,
        task_repo=TaskRepository(session, user_id),
    )


@register_patch_hook("tasks")
def tasks_patch_hook(
    item: Any, data: Any, session: Session, current_user: User
) -> dict[str, Any]:  # noqa: ANN401,ARG001
    """Invoked by generalized PATCH route to re-calculate tasks progress upon changes."""
    tasks_service = create_tasks_service(
        session, current_user.id, current_user.timezone
    )
    progress = tasks_service.calculate_tasks_progress_today()
    return {"progress": progress}
