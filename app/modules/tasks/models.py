# Handles DB models for tasks module

#from app.database import Base
from app.base import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

# Task Model for database of tasks, with varying types (task vs habit, etc)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    is_done = Column(Boolean, default=False)
    type = Column(String(50), default='todo')
    is_anchor = Column(Boolean, default=False)
    created_at = (Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))
    completed_at = (Column(DateTime(timezone=True), nullable=True))

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