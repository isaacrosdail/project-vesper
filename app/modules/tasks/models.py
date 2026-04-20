"""
Database models for the Tasks module.
"""
from datetime import datetime
from enum import StrEnum, auto
from typing import ClassVar

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Index,
    Table,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base, CustomBaseTaskMixin
from app.shared.datetime_.helpers import convert_to_timezone
from app.shared.models import task_pillars, task_tags
from app.shared.serialization import APISerializable

TASK_NAME_MAX_LENGTH = 150


# Association table for task_links
# PKey for each means the link itself forms a composite key:
# (subtask_id, supertask_id)
task_links = Table(
    "task_links",
    Base.metadata,
    Column("subtask_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("supertask_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
)

class PriorityEnum(StrEnum):
    LOW =auto()
    MEDIUM = auto()
    HIGH = auto()
    FROG = auto()

    def __lt__(self, other: str) -> bool:
        order = list(PriorityEnum)
        return order.index(self) < order.index(PriorityEnum(other))


class Task(Base, CustomBaseTaskMixin, APISerializable):
    __api_exclude__: ClassVar[list[str]] = []
    __api_properties__: ClassVar[list[str]] = ["is_done"]

    __table_args__ = (
        CheckConstraint(
            "priority != 'frog' OR due_date IS NOT NULL", name="frog_requires_due_date"
        ),
        UniqueConstraint("user_id", "name", name="uq_user_task_name"),
        Index("ix_tasks_user_due_date", "user_id", "due_date"),
    )

    name: Mapped[str] = mapped_column(String(TASK_NAME_MAX_LENGTH), nullable=False)

    priority: Mapped[PriorityEnum] = mapped_column(
        SAEnum(PriorityEnum, name="priority_enum", values_callable=lambda x: [e.value for e in x]), # db stores lowercase too
        nullable=False # now false since we made is_frog not a thing anymore -> thats now a priority
    )

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Facilitates relationships to multiple super/subtasks
    supertasks = relationship(
        "Task",
        secondary=task_links,
        primaryjoin=lambda: Task.id == task_links.c.subtask_id,
        secondaryjoin=lambda: Task.id == task_links.c.supertask_id,
        back_populates="subtasks",
    )

    subtasks = relationship(
        "Task",
        secondary=task_links,
        primaryjoin=lambda: Task.id == task_links.c.supertask_id,
        secondaryjoin=lambda: Task.id == task_links.c.subtask_id,
        back_populates="supertasks",
    )

    pillars = relationship("Pillar", secondary=task_pillars, back_populates="tasks", lazy="selectin")

    # Works as a Python property on instances AND as an SQL expression in queries:
    # task.is_done rets True/False, and Task.is_done == True in a .where() generates completed_at IS NOT NULL in SQL
    # can't desync
    @hybrid_property
    def is_done(self) -> bool:
        return self.completed_at is not None

    @property
    def is_frog(self) -> bool:
        return self.priority is PriorityEnum.FROG

    @property
    def due_date_local(self) -> datetime | None:
        return (
            convert_to_timezone(self.user.timezone, self.due_date)
            if self.due_date
            else None
        )

    user = relationship("User", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return f"<Task id={self.id} name='{self.name}'>"
