"""
Database models for the Tasks module.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, CheckConstraint, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app._infra.db_base import Base, CustomBaseTaskMixin
from app.modules.tasks.constants import TASK_NAME_MAX_LENGTH
from app.shared.models import Tag, task_tags
from app.shared.serialization import APISerializable
from app.shared.types import OrderedEnum


class PriorityEnum(OrderedEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# NOTE: Hacky, but lets us inherit OrderedEnum and define custom sort order
PriorityEnum.sort_order = ["HIGH", "MEDIUM", "LOW"] # type: ignore[attr-defined]

class Task(Base, CustomBaseTaskMixin, APISerializable):

    __api_exclude__: list[str] = []

    __table_args__ = (
        CheckConstraint(
            "NOT is_frog OR due_date IS NOT NULL",
            name='ck_task_frog_requires_due_date'
        ),
        CheckConstraint(
            "(is_frog = true AND priority IS NULL) OR (NOT is_frog AND priority IS NOT NULL)",
            name='ck_frog_priority_mutually_exclusive'
        ),
        UniqueConstraint('user_id', 'name', name='uq_user_task_name'),
    )

    name: Mapped[str] = mapped_column(
        String(TASK_NAME_MAX_LENGTH),
        nullable=False
    )

    priority: Mapped[PriorityEnum] = mapped_column(
        SAEnum(PriorityEnum, name="priority_enum"),
        nullable=True
    )

    is_frog: Mapped[bool] = mapped_column(Boolean, default=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

    def __str__(self) -> str:
        return str(self.name)
    
    def __repr__(self) -> str:
        return f"<Task id={self.id} name='{self.name}'>"
