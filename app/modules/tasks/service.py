from datetime import datetime, time, timedelta, date
from zoneinfo import ZoneInfo

from app.modules.tasks.repository import TasksRepository
from app.shared.datetime.helpers import day_range_utc
from app.api.responses import service_response


class TasksService:
    def __init__(self, repository: TasksRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz


    def save_task(self, typed_data: dict, task_id: int | None):

        # Attach due_date datetime
        typed_data["due_date"] = self.to_eod_datetime(typed_data.get("due_date"), self.user_tz)

        # Check for existing frog task
        if typed_data["is_frog"]:
            start_utc, end_utc = day_range_utc(typed_data["due_date"].date(), self.user_tz)

            existing_frog = self.repo.get_frog_task_in_window(start_utc, end_utc)
            if existing_frog:
                return service_response(
                    False,
                    "Error: Duplicate frog task",
                    errors={"frog_task": [f"You already have a 'frog' task for {typed_data["due_date"].date().isoformat()}"]}
                )

        ### UPDATE
        if task_id:
            task = self.repo.get_task_by_id(task_id)
            if not task:
                return service_response(False, "Task not found")
            
            # Update fields
            for field, value in typed_data.items():
                setattr(task, field, value)
            
            return service_response(True, "Task updated", data={"task": task})

        else:
            ### CREATE
            task = self.repo.create_task(
                name=typed_data["name"],
                priority=typed_data.get("priority"),
                due_date=typed_data.get("due_date"),
                is_frog=typed_data["is_frog"]
            )
            return service_response(True, "Task added", data={"task": task})


    def to_eod_datetime(self, date: date | None, tz_str: str) -> datetime | None:
        """Convert a date to exclusive EOD datetime in given timezone."""
        if not date:
            return None
        tz = ZoneInfo(tz_str)
        start_of_day = datetime.combine(date, time.min, tzinfo=tz)
        return start_of_day + timedelta(days=1)