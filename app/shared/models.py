
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.habits.models import Habit
    from app.modules.tasks.models import Task
    from app.modules.time_tracking.models import TimeEntry

from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base

TAG_NAME_MAX_LENGTH = 50
TAG_SCOPE_MAX_LENGTH = 20


# Tasks association table
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# Habits association table
habit_tags = Table(
    "habit_tags",
    Base.metadata,
    Column("habit_id", ForeignKey("habits.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    """A user-defined label attachable to tasks and habits."""

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_tag_name"),)

    name: Mapped[str] = mapped_column(String(TAG_NAME_MAX_LENGTH), nullable=False)

    scope: Mapped[str] = mapped_column(
        String(TAG_SCOPE_MAX_LENGTH), default="universal"
    )

    tasks: Mapped[list[Task]] = relationship("Task", secondary="task_tags", back_populates="tags")
    habits: Mapped[list[Habit]] = relationship("Habit", secondary="habit_tags", back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name='{self.name}'>"


habit_pillars = Table(
    "habit_pillars",
    Base.metadata,
    Column("habit_id", ForeignKey("habits.id", ondelete="CASCADE"), primary_key=True),
    Column("pillar_id", ForeignKey("pillars.id", ondelete="CASCADE"), primary_key=True)
)

task_pillars = Table(
    "task_pillars",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("pillar_id", ForeignKey("pillars.id", ondelete="CASCADE"), primary_key=True)
)

time_entry_pillars = Table(
    "time_entry_pillars",
    Base.metadata,
    Column("time_entry_id", ForeignKey("time_entries.id", ondelete="CASCADE"), primary_key=True),
    Column("pillar_id", ForeignKey("pillars.id", ondelete="CASCADE"), primary_key=True)
)

class Pillar(Base):
    """A core life-domain (Health, Career, etc) that activities roll up into."""

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_pillar_name"),)

    name: Mapped[str] = mapped_column(String(30), nullable=False)

    habits: Mapped[list[Habit]] = relationship("Habit", secondary=habit_pillars, back_populates="pillars")
    tasks: Mapped[list[Task]] = relationship("Task", secondary=task_pillars, back_populates="pillars")
    time_entries: Mapped[list[TimeEntry]] = relationship("TimeEntry", secondary=time_entry_pillars, back_populates="pillars")

    def __repr__(self) -> str:
        return f"<Pillar id={self.id} name='{self.name}'>"

