
from sqlalchemy import ForeignKey, Table, Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app._infra.db_base import Base
from app.modules.tasks.constants import TAG_NAME_MAX_LENGTH, TAG_SCOPE_MAX_LENGTH

# Tasks association table (many-to-many link between tasks & tags)
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("task.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

# Habits association table
habit_tags = Table(
    "habit_tags",
    Base.metadata,
    Column("habit_id", ForeignKey("habit.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Tag(Base):

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_tag_name'),
    )

    name = Column(String(TAG_NAME_MAX_LENGTH), nullable=False)
    scope = Column(String(TAG_SCOPE_MAX_LENGTH), default="universal")

    # Reciprocal relationships for many-to-many
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")
    habits = relationship("Habit", secondary="habit_tags", back_populates="tags")

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Tag id={self.id} name='{self.name}'>"