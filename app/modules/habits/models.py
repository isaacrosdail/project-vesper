"""
Model definitions for Habits module.
"""

from datetime import datetime, timezone
from enum import StrEnum, auto

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.datetime_.helpers import convert_to_timezone
from app.shared.models import Pillar, habit_pillars, habit_tags

HABIT_NAME_MAX_LENGTH = 100
LC_TITLE_MAX_LENGTH = 200

PROMOTION_THRESHOLD = 0.7 ## TODO: lives here for time being

class StatusEnum(StrEnum):
    EXPERIMENTAL = auto()
    ESTABLISHED = auto()


class Habit(Base):

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_habit_name"),
        CheckConstraint(
            "established_date IS NULL OR status = 'established'",
            name="established_requires_established_status",
        ),
    )

    name: Mapped[str] = mapped_column(String(HABIT_NAME_MAX_LENGTH), nullable=False)

    status: Mapped[StatusEnum | None] = mapped_column(
        SAEnum(StatusEnum, name="status_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )

    established_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Represents target completion rate per week
    target_frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    @property
    def established_date_local(self) -> datetime | None:
        return (
            convert_to_timezone(self.user.timezone, self.established_date)
            if self.established_date
            else None
        )

    user = relationship("User", back_populates="habits")
    tags = relationship("Tag", secondary=habit_tags, back_populates="habits")
    pillars = relationship("Pillar", secondary=habit_pillars, back_populates="habits", lazy="selectin")
    habit_completions = relationship(
        "HabitCompletion", back_populates="habit", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base):
    """Stores each completion as a new entry, enabling better analytics."""

    __table_args__ = (
        Index("ix_habit_completions_user_habit_completed_on", "user_id", "habit_id", "completed_on"),
        UniqueConstraint("habit_id", "completed_on", name="uq_habit_completions_habit_id_completed_on"),
    )

    completed_on: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    habit: Mapped[Habit] = relationship("Habit", back_populates="completions")

    def __repr__(self) -> str:
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"

