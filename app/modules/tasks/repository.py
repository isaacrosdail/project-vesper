"""
Repository layer for Tasks module.
"""

from app.shared.repository.base import BaseRepository

from .models import Task


class TasksRepository(BaseRepository):

    def get_all_tasks(self):
        """Return all tasks for current user."""
        return self.session.query(Task).filter(
            Task.user_id==self.user_id
        ).all()
    
    def create_task(self, name: str):
        """Create & add a new task. Returns said task."""
        new_task = Task(
            user_id=self.user_id,
            name=name
        )
        self.session.add(new_task)
        return new_task