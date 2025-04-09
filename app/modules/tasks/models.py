# Handles DB models for tasks module

from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

# Task Model for database of tasks, with varying types (task vs habit, etc)
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    is_done = Column(Boolean, default=False)
    type = Column(String(50), default='todo')
    created_at = (Column(DateTime, default=datetime.now))
    completed_at = (Column(DateTime, nullable=True))

    # Human-readable column names
    COLUMN_LABELS = {
        "id": "Task ID",
        "title": "Task",
        "is_done": "Status",
        "type": "Type",
        "created_at": "Created",
        "completed_at": "Completed"
    }