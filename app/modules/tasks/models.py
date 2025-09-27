"""
Database models for the Tasks module.
"""
import enum

from sqlalchemy import Boolean, Column, DateTime, String, CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app._infra.db_base import Base, CustomBaseTaskMixin
from app.modules.tasks.constants import TASK_NAME_MAX_LENGTH
from app.shared.models import Tag, task_tags

class PriorityEnum(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Task(Base, CustomBaseTaskMixin):

    __table_args__ = (
        CheckConstraint(
            "NOT is_frog OR due_date IS NOT NULL",
            name='ck_task_frog_requires_due_date'
        ),
    )

    name = Column(
        String(TASK_NAME_MAX_LENGTH),
        unique=True,
        nullable=False
    )

    priority = Column(
        SAEnum(PriorityEnum, name="priority_enum"),
        default=PriorityEnum.MEDIUM,
        nullable=False
    )

    is_frog = Column(Boolean, default=False)
    is_done = Column(Boolean, default=False)
    due_date = Column(DateTime(timezone=True), nullable=True)

    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Task id={self.id} name='{self.name}'>"