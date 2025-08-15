"""
Database models for the Tasks module.
"""
import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Table
from sqlalchemy.orm import relationship

from app._infra.db_base import Base, CustomBaseTaskMixin

# Association table (many-to-many link between tasks & tags)
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("task.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Priority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Tag(Base):
    name = Column(String(50), unique=True, nullable=False)
    scope = Column(String(20), default="universal")

    # Reciprocal relationships for many-to-many
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")
    habits = relationship("Habit", secondary="habit_tags", back_populates="tags")

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Tag id={self.id} name='{self.name}'>"

class Task(Base, CustomBaseTaskMixin):

    name = Column(String(255), unique=True, nullable=False)
    is_done = Column(Boolean, default=False)
    priority = Column(SAEnum(Priority), default=Priority.medium, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)

    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")
    
    VISIBLE_COLUMNS = {
        "name", "is_done", "priority", "due_date", "created_at", "completed_at"
    }

    # Human-readable column names
    COLUMN_LABELS = {
        "id": "Task ID",
        "name": "Task",
        "is_done": "Status",
        "priority": "Priority",
        "due_date": "Due Date",
        "created_at": "Created",
        "completed_at": "Completed",
    }

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Task id={self.id} name='{self.name}'>"
    
    # TODO: NOTES: First arg is the class (cls) instead of the instance (self)
    # Used when the method works with class-level data (metadata, config, alt constructors)
    @classmethod
    def build_columns(cls) -> list[dict]:
        """
        Builds a list of column definitions for use as table headers.
        Respects the order defined in `VISIBLE_COLUMNS` & excludes fields not explicitly whitelisted.
        """
        return [{"key": c, "label": cls.COLUMN_LABELS.get(c, c)} for c in cls.VISIBLE_COLUMNS]