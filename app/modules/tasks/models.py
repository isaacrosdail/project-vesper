# Handles DB models for tasks module

from app.core.db_base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Task Model for database of tasks, with varying types (task vs habit, etc)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True, nullable=False)
    is_done = Column(Boolean, default=False)
    type = Column(String(50), default='todo')
    is_anchor = Column(Boolean, default=False)
    created_at = (Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))
    completed_at = (Column(DateTime(timezone=True), nullable=True))

    # Lets us convert to London time simply by doing task.created_at_local
    # as if it were a column in the table / property of the object
    @property
    def created_at_local(self):
        return self.created_at.astimezone(ZoneInfo("Europe/London"))
    
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "Task ID",
        "title": "Task",
        "is_done": "Status",
        "type": "Type",
        "is_anchor": "Anchor Habit?",
        "created_at": "Created",
        "completed_at": "Completed"
    }