# Handles DB models for tasks module

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.db_base import Base


# Task Model for database of tasks, with varying types (task vs habit, etc)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True, nullable=False)
    is_done = Column(Boolean, default=False)
    type = Column(String(50), default='todo')
    created_at = (Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))
    completed_at = (Column(DateTime(timezone=True), nullable=True))

    # @property is a common decorator for creating "virtual attributes" that are computed on-the-fly
    # Lets us convert to London time simply by doing task.created_at_local
    # as if it were a column in the model itself
    @property
    def created_at_local(self):
        return self.created_at.astimezone(ZoneInfo("Europe/London"))
    
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "Task ID",
        "title": "Task",
        "is_done": "Status",
        "type": "Type",
        "created_at": "Created",
        "completed_at": "Completed"
    }