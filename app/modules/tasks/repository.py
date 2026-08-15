"""
Repository layer for Tasks module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session

from sqlalchemy import select

from app.modules.tasks.models import PriorityEnum, Task, task_links
from app.shared.repository.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Task)

    def create_task(
        self,
        *,
        name: str,
        priority: PriorityEnum | None,
        due_datetime: datetime | None = None,
        sort_key: str
    ) -> Task:
        """Create & add a new task. Returns said task."""
        task = Task(
            user_id=self.user_id,
            name=name,
            priority=priority,
            due_datetime=due_datetime,
            sort_key=sort_key
        )
        return self.add(task)

    def get_all_regular_tasks(self) -> list[Task]:
        stmt = self._user_select(Task).where(Task.priority != PriorityEnum.FROG)
        return list(self.session.scalars(stmt).all())

    def get_all_links(self) -> list[tuple[int, int]]:
        return [
            (row.subtask_id, row.supertask_id) for row
            in self.session.execute(select(task_links)).all()
        ]

    def get_frog_task_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> Task | None:
        """Return frog task in given window, or None."""
        stmt = self._user_select(Task).where(
            Task.priority == PriorityEnum.FROG,
            Task.due_datetime >= start_utc,
            Task.due_datetime < end_utc
        )
        return self.session.scalars(stmt).first()

    def get_max_sort_key(self) -> str | None:
        stmt = (
            select(Task.sort_key)
            .where(Task.user_id == self.user_id)
            .order_by(Task.sort_key.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()
