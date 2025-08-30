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
    
    def get_all_regular_tasks(self):
        return self.session.query(Task).filter(
            Task.user_id==self.user_id,
            Task.is_frog==False
        ).all()
    
    def get_today_frog(self):
        """Return today's frog task, or None."""
        today = convert_to_timezone(self.user_tz).date() # user's today
        start_utc, end_utc = day_range(today, self.user_tz) # UTC bounds
        return self.session.query(Task).filter(
            Task.user_id == self.user_id,
            Task.is_frog == True,
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        ).first()
    
    def create_task(self, name: str, priority: Priority = Priority.medium, due_date: datetime | None = None, is_frog: bool | None = None):
        """Create & add a new task. Returns said task."""

        if is_frog:
            if due_date is None:
                # default to today in user's timezone
                today = convert_to_timezone(self.user_tz).date()
                due_date = datetime.combine(today, time(23, 59, 59)).replace(tzinfo=ZoneInfo(self.user_tz))
            self._assert_no_existing_frog(due_date)
        
        new_task = Task(
            user_id=self.user_id,
            name=name,
            is_frog=is_frog,
            due_date=due_date,
            priority=priority
        )
        self.session.add(new_task)
        return new_task
    
    def _assert_no_existing_frog(self, task_date: datetime):
        """Check for pre-existing 'frog' task. Default to today (in user's timezone) if no task_date is specified."""
        user_date = task_date.astimezone(ZoneInfo(self.user_tz)).date()
        start_utc, end_utc = day_range(user_date, self.user_tz)
        
        existing = self.session.query(Task).filter(
            Task.user_id == self.user_id,
            Task.is_frog == True,
            Task.due_date >= start_utc,
            Task.due_date < end_utc
        ).first()

        if existing:
            raise ValueError(f"You already have a 'frog' task for {task_date.isoformat()}.")