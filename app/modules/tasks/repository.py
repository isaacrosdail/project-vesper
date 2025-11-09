"""
Repository layer for Tasks module.
"""

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime

from app.modules.tasks.models import PriorityEnum, Task
from app.shared.repository.base import BaseRepository


class TasksRepository(BaseRepository[Task]):
    def __init__(self, session: 'Session', user_id: int, user_tz: str):
        super().__init__(session, user_id, user_tz, model_cls=Task)

    def create_task(self, name: str, is_frog: bool, priority: PriorityEnum | None, due_date: datetime | None = None) -> Task:
        """Create & add a new task. Returns said task."""
        task = Task(
            user_id=self.user_id,
            name=name,
            priority=priority,
            is_frog=is_frog,
            due_date=due_date
        )
        return self.add(task)

    def get_all_regular_tasks(self) -> list[Task]:
        stmt = self._user_select(Task).where(
            Task.is_frog == False
        )
        return list(self.session.execute(stmt).scalars().all())
    
    def get_all_tasks_in_window(self, start_utc: datetime, end_utc: datetime) -> list[Task]:
        stmt = self._user_select(Task).where(
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        )
        return list(self.session.execute(stmt).scalars().all())
    
    def get_frog_task_in_window(self, start_utc: datetime, end_utc: datetime) -> Task | None:
        """Return frog task in given window, or None."""
        stmt = self._user_select(Task).where(
            Task.is_frog == True,
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        )
        result = self.session.execute(stmt).scalars().first()
        return cast(Task | None, result)



