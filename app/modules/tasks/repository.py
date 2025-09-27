"""
Repository layer for Tasks module.
"""

from app.shared.repository.base import BaseRepository
from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.shared.datetime.helpers import now_utc, day_range_utc, convert_to_timezone
from app.modules.tasks.models import Task, PriorityEnum


class TasksRepository(BaseRepository):
    def __init__(self, session, user_id, user_tz):
        super().__init__(session, user_id, user_tz, model_cls=Task)


    def get_all_tasks(self):
        return self.get_all()

    def get_all_regular_tasks(self):
        return self._user_query(Task).filter(
            Task.is_frog == False
        ).all()
    
    def get_frog_task_in_window(self, start_utc, end_utc):
        """Return frog task in given window, or None."""
        return self._user_query(Task).filter(
            Task.is_frog == True,
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        ).first()
    
    def get_task_by_id(self, task_id: int):
        return self.get_by_id(task_id)
    
    def create_task(self, name: str, priority: PriorityEnum = PriorityEnum.MEDIUM, due_date: datetime | None = None, is_frog: bool | None = None):
        """Create & add a new task. Returns said task."""
        task = Task(
            user_id=self.user_id,
            name=name,
            is_frog=is_frog,
            due_date=due_date,
            priority=priority
        )
        return self.add(task)
    
    # TODO
    def _assert_no_existing_frog(self, task_date: datetime):
        """Check for pre-existing 'frog' task. Default to today (in user's timezone) if no task_date is specified."""
        user_date = task_date.astimezone(ZoneInfo(self.user_tz)).date()
        start_utc, end_utc = day_range_utc(user_date, self.user_tz)
        
        existing = self.session.query(Task).filter(
            Task.user_id == self.user_id,
            Task.is_frog == True,
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        ).first()

        if existing:
            raise ValueError(f"You already have a 'frog' task for {task_date.isoformat()}.")