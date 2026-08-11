"""
Database models for the Tasks module.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base, CustomBaseTaskMixin
from app.shared.models import Pillar, Tag, task_pillars, task_tags

TASK_NAME_MAX_LENGTH = 150


task_links = Table(
    "task_links",
    Base.metadata,
    Column("subtask_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("supertask_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
)

class PriorityEnum(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    FROG = auto()

    def __lt__(self, other: str) -> bool:
        order = list(PriorityEnum)
        return order.index(self) < order.index(PriorityEnum(other))


class Task(Base, CustomBaseTaskMixin):

    __table_args__ = (
        CheckConstraint(
            "priority != 'frog' OR due_date IS NOT NULL", name="frog_requires_due_date"
        ),
        Index(
            "uq_user_task_name",
            "user_id", "name",
            unique=True,
            postgresql_where=text("completed_at IS NULL"),
        ),
        Index("ix_tasks_user_due_date", "user_id", "due_date"),
    )

    name: Mapped[str] = mapped_column(String(TASK_NAME_MAX_LENGTH), nullable=False)

    priority: Mapped[PriorityEnum] = mapped_column(
        SAEnum(PriorityEnum, name="priority_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # collation="C" ensures sort_key comparisons/sorting always use C collation rules by Postgres/DB.
    # collate("C") so postgres uses bytewise collation (to align with JS)
    # No index due to scale; if large N, add composite (user_id, sort_key), inherits C from the column.
    sort_key: Mapped[str] = mapped_column(String(collation="C"), nullable=False)

    supertasks: Mapped[list[Task]] = relationship(
        "Task",
        secondary=task_links,
        primaryjoin=lambda: Task.id == task_links.c.subtask_id,
        secondaryjoin=lambda: Task.id == task_links.c.supertask_id,
        back_populates="subtasks",
        lazy="selectin",
    )
    subtasks: Mapped[list[Task]] = relationship(
        "Task",
        secondary=task_links,
        primaryjoin=lambda: Task.id == task_links.c.supertask_id,
        secondaryjoin=lambda: Task.id == task_links.c.subtask_id,
        back_populates="supertasks",
        lazy="selectin",
    )
    pillars: Mapped[list[Pillar]] = relationship("Pillar", secondary=task_pillars, back_populates="tasks", lazy="selectin")
    tags: Mapped[list[Tag]] = relationship("Tag", secondary=task_tags, back_populates="tasks", lazy="selectin")

    @hybrid_property
    def is_done(self) -> bool:
        return self.completed_at is not None

    @property
    def is_frog(self) -> bool:
        return self.priority is PriorityEnum.FROG

    def __repr__(self) -> str:
        return f"<Task id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return str(self.name)

    def is_overdue(self, now: datetime) -> bool:
        return not self.is_done and self.due_date is not None and self.due_date < now

