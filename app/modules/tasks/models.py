"""
Database models for the Tasks module.
"""

from app._infra.db_base import Base, CustomBaseTaskMixin
from sqlalchemy import Boolean, Column, String


# Task Model for database of tasks, with varying types (task vs habit, etc)
class Task(Base, CustomBaseTaskMixin):

    title = Column(String(255), unique=True, nullable=False)
    is_done = Column(Boolean, default=False)
    type = Column(String(50), default='todo')
    # TODO: Add category, due_date?
    
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "Task ID",
        "title": "Task",
        "is_done": "Status",
        "type": "Type",
        "created_at": "Created",
        "completed_at": "Completed"
    }