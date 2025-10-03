"""
Repository layer for Tasks module.
"""

from datetime import datetime

from app.modules.tasks.models import PriorityEnum, Task
from app.shared.repository.base import BaseRepository


class TasksRepository(BaseRepository):
    def __init__(self, session, user_id, user_tz):
        super().__init__(session, user_id, user_tz, model_cls=Task)


    def get_all_tasks(self):
        return self.get_all()

    def get_all_regular_tasks(self):
        return self._user_query(Task).filter(
            Task.is_frog == False
        ).all()
    
    def get_frog_task_in_window(self, start_utc: datetime, end_utc: datetime):
        """Return frog task in given window, or None."""
        return self._user_query(Task).filter(
            Task.is_frog == True,
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        ).first()
    
    def get_task_by_id(self, task_id: int):
        return self.get_by_id(task_id)
    
    def create_task(self, name: str, is_frog: bool, priority: PriorityEnum | None, due_date: datetime | None = None):
        """Create & add a new task. Returns said task."""
        task = Task(
            user_id=self.user_id,
            name=name,
            priority=priority,
            is_frog=is_frog,
            due_date=due_date
        )
        return self.add(task)
