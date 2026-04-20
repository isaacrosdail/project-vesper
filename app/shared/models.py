

from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base

TAG_NAME_MAX_LENGTH = 50
TAG_SCOPE_MAX_LENGTH = 20


# Tasks association table (many-to-many link between tasks & tags)
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

# Habits association table
habit_tags = Table(
    "habit_tags",
    Base.metadata,
    Column("habit_id", ForeignKey("habits.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_tag_name"),)

    name: Mapped[str] = mapped_column(String(TAG_NAME_MAX_LENGTH), nullable=False)

    scope: Mapped[str] = mapped_column(
        String(TAG_SCOPE_MAX_LENGTH), default="universal"
    )

    # Reciprocal relationships for many-to-many
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")
    habits = relationship("Habit", secondary="habit_tags", back_populates="tags")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name='{self.name}'>"


habit_pillars = Table(
    "habit_pillars",
    Base.metadata,
    Column("habit_id", ForeignKey("habits.id"), primary_key=True),
    Column("pillar_id", ForeignKey("pillars.id"), primary_key=True)
)

task_pillars = Table(
    "task_pillars",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("pillar_id", ForeignKey("pillars.id"), primary_key=True)
)

time_entry_pillars = Table(
    "time_entry_pillars",
    Base.metadata,
    Column("time_entry_id", ForeignKey("time_entries.id"), primary_key=True),
    Column("pillar_id", ForeignKey("pillars.id"), primary_key=True)
)

class Pillar(Base):
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_pillar_name"),)

    name: Mapped[str] = mapped_column(String(30), nullable=False)

    habits = relationship("Habit", secondary=habit_pillars, back_populates="pillars")
    tasks = relationship("Task", secondary=task_pillars, back_populates="pillars")
    time_entries = relationship("TimeEntry", secondary=time_entry_pillars, back_populates="pillars")

    def __repr__(self) -> str:
        return f"<Pillar id={self.id} name='{self.name}'>"

