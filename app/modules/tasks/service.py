import sys
from datetime import datetime, time, timedelta, date
from zoneinfo import ZoneInfo

from app.modules.tasks.repository import TasksRepository
from app.shared.datetime.helpers import day_range_utc, today_range_utc, now_utc, is_same_local_date
from app.api.responses import service_response
from app.shared.hooks import register_patch_hook


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
        eod_midnight = start_of_day + timedelta(days=1)
        return eod_midnight - timedelta(seconds=1)
    
    def calculate_tasks_progress_today(self):

        # Get today's window
        start_utc, end_utc = today_range_utc(self.user_tz)

        # Fetch all tasks
        all_tasks = self.repo.get_all_tasks()
        count_today = len(all_tasks)

        # Count completed vs expected for today
        num_completed = 0
        num_expected = 0

        for task in all_tasks:
            due_today = task.due_date and is_same_local_date(task.due_date, self.user_tz)
            completed_today = task.completed_at and is_same_local_date(task.completed_at, self.user_tz)

            if due_today:
                num_expected += 1
                if completed_today:
                    num_completed += 1

            elif completed_today and task.due_date is None:
                # "spontaneous" task, completed today without a due date
                num_completed += 1
                num_expected += 1

        # Completion percentage
        percent_complete = (num_completed / num_expected * 100) if num_expected > 0 else 0

        return start_utc, end_utc, num_completed, num_expected, percent_complete


# Gets invoked by generalized PATCH route 
@register_patch_hook('tasks')
def tasks_patch_hook(item, data, session, current_user):
    repo = TasksRepository(session, current_user.id, current_user.timezone)
    service = TasksService(repo, current_user.timezone)
    progress = service.calculate_tasks_progress_today()
    return {"progress": progress}