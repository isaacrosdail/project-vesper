
from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.repository import TasksRepository
from app.shared.datetime.helpers import day_range_utc, parse_eod_datetime_from_date
from app.modules.tasks.validators import validate_task
from app.modules.api.responses import service_response


class TasksService:
    def __init__(self, repository: TasksRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz
    
    def create_task(self, task_data: dict):

        errors = validate_task(task_data)
        if errors:
            return service_response(False, "Validation failed", errors=errors)


        # Parse due_date "2025-09-22" -> datetime(2025, 9, 22, 23:59:59, tz=user_tz)
        due_date = (
            parse_eod_datetime_from_date(task_data["due_date"], self.user_tz)
            if task_data["due_date"]
            else None
        )

        # check if existing frog task
        if task_data.get("is_frog") and due_date:
            start_utc, end_utc = day_range_utc(due_date.date(), self.user_tz)

            existing_frog = self.repo.get_frog_task_in_window(start_utc, end_utc)
            if existing_frog:
                return service_response(
                    False,
                    "Validation failed",
                    errors={"frog_task": [f"You already have a 'frog' task for {due_date.date().isoformat()}"]}
                )
        
        # Typecasts
        prepped_data = {
            **task_data,
            "priority": PriorityEnum(task_data["priority"]),
            "is_frog": bool(task_data["is_frog"]),
            "due_date": due_date
        }

        task = self.repo.create_task(**prepped_data)
        return service_response(True, "Task added", data={"task": task})