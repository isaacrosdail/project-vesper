
from typing import cast

from sqlalchemy import ForeignKey, Table, Column, String, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app._infra.db_base import Base
from app.modules.tasks.constants import TAG_NAME_MAX_LENGTH, TAG_SCOPE_MAX_LENGTH

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

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )

    name: Mapped[str] = mapped_column(String(TAG_NAME_MAX_LENGTH), nullable=False)
    scope: Mapped[str] = mapped_column(String(TAG_SCOPE_MAX_LENGTH), default="universal")

    # Reciprocal relationships for many-to-many
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")
    habits = relationship("Habit", secondary="habit_tags", back_populates="tags")

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"<Tag id={self.id} name='{self.name}'>"