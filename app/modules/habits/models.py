"""
Model definitions for Habits module.
"""
from __future__ import annotations

from datetime import date  # noqa: TC003
from enum import StrEnum, auto

from sqlalchemy import (
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.models import Pillar, Tag, habit_pillars, habit_tags
from app.shared.target import Target

HABIT_NAME_MAX_LENGTH = 100

class HabitTypeEnum(StrEnum):
    BINARY = auto()
    NUMERIC_VALUE = auto()
    DURATION = auto()


class Habit(Base):

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_habit_name"),
        CheckConstraint(
            "(type = 'binary' AND num_nonnulls(target_low, target_high, units) = 0) " \
            "OR (type = 'numeric_value') " \
            "OR (type = 'duration' AND units IS NULL)",
            name="habit_type_shapes",
        ),
        CheckConstraint(
            "weekly_frequency BETWEEN 1 AND 7",
            name="weekly_frequency_range"
        ),
        CheckConstraint("target_low > 0 AND target_high > 0", name="target_positive"),
        CheckConstraint("target_low <= target_high", name="low_le_high"),
    )

    name: Mapped[str] = mapped_column(String(HABIT_NAME_MAX_LENGTH), nullable=False)

    # Represents target completion rate per week
    weekly_frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    target_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_high: Mapped[float | None] = mapped_column(Float, nullable=True)

    type: Mapped[HabitTypeEnum] = mapped_column(
        SAEnum(HabitTypeEnum, name="habit_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    units: Mapped[str | None] = mapped_column(String(50), nullable=True)


    tags: Mapped[list[Tag]] = relationship("Tag", secondary=habit_tags, back_populates="habits", lazy="selectin")
    pillars: Mapped[list[Pillar]] = relationship(
        "Pillar", secondary=habit_pillars, back_populates="habits", lazy="selectin"
    )
    completions: Mapped[list[HabitCompletion]] = relationship(
        "HabitCompletion", back_populates="habit", cascade="all, delete-orphan", lazy="raise",
        passive_deletes=True
    )

    @property
    def target(self) -> Target | None:
        if self.target_low is None and self.target_high is None:
            return None
        return Target(self.target_low, self.target_high)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base):
    """Stores each completion as a new entry, enabling better analytics."""

    __table_args__ = (
        Index("ix_habit_completions_user_habit_entry_date", "user_id", "habit_id", "entry_date"),
        UniqueConstraint("habit_id", "entry_date", name="uq_habit_completions_habit_id_entry_date"),
        CheckConstraint(
            "num_nonnulls(target_low_snapshot, target_high_snapshot) = 0 OR value IS NOT NULL",
            name="snapshot_requires_value",
        ),
        CheckConstraint("value >= 0", name="value_nonnegative"),
        CheckConstraint("target_low_snapshot > 0 AND target_high_snapshot > 0", name="snapshot_targets_positive"),
        CheckConstraint("target_low_snapshot <= target_high_snapshot", name="low_snapshot_le_high_snapshot"),
    )

    entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_low_snapshot: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_high_snapshot: Mapped[float | None] = mapped_column(Float, nullable=True)


    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    habit: Mapped[Habit] = relationship("Habit", back_populates="completions")

    @property
    def target(self) -> Target | None:
        if self.target_low_snapshot is None and self.target_high_snapshot is None:
            return None
        return Target(self.target_low_snapshot, self.target_high_snapshot)

    @property
    def satisfied(self) -> bool:
        if self.value is None:
            return True
        return Target(self.target_low_snapshot, self.target_high_snapshot).satisfied(self.value)

    def __repr__(self) -> str:
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"

