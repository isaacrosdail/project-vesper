# Handles DB models for tasks module

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.db_base import Base, CustomBaseTaskMixin


# Task Model for database of tasks, with varying types (task vs habit, etc)
class Task(Base, CustomBaseTaskMixin):

    title = Column(String(255), unique=True, nullable=False)
    is_done = Column(Boolean, default=False)
    type = Column(String(50), default='todo')
    
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "Task ID",
        "title": "Task",
        "is_done": "Status",
        "type": "Type",
        "created_at": "Created",
        "completed_at": "Completed"
    }