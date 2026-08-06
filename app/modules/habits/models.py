"""
Model definitions for Habits module.
"""
from __future__ import annotations

from datetime import date, datetime  # noqa: TC003
from enum import StrEnum, auto
from typing import assert_never

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.models import Pillar, Tag, habit_pillars, habit_tags
from app.shared.target import AtLeast, AtMost, Target, Within, is_met

HABIT_NAME_MAX_LENGTH = 100

class HabitTypeEnum(StrEnum):
    BINARY = auto()
    NUMERIC_VALUE = auto()
    DURATION = auto()

class TargetKind(StrEnum):
    AT_LEAST = auto()
    AT_MOST = auto()
    WITHIN = auto()


## TODO: when working, move to target.py:
def build_target(kind: TargetKind | None, value: float | None, tolerance: float | None) -> Target | None:
    if kind is None:
        return None
    if value is None:
        raise ValueError("target kind without target value")
    match kind:
        case TargetKind.AT_LEAST: return AtLeast(value)
        case TargetKind.AT_MOST: return AtMost(value)
        case TargetKind.WITHIN:
            if tolerance is None:
                raise ValueError("within target without tolerance")
            return Within(value, tolerance)
        case _: assert_never(kind)


# type Target =
#   | { kind: 'at_least' | 'at_most'; value: number }
#   | { kind: 'within'; value: number; tolerance: number }

# type Habit =
#   | { type: 'binary' }
#   | { type: 'numeric_value'; units?: string; target: Target | null }  // null = "any value"

# type Completion = {
#   entry_date: string
#   value: number | null            // what was logged; null for binary
#   target_snapshot: Target | null  // the goal as it stood at logging time
# }


class Habit(Base):

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_habit_name"),
        # Encode the habit-type discriminated union. Shapes must stay in sync with the Target union (app/shared/target.py) & Pydantic schemas.
        CheckConstraint(
            "(type = 'binary' AND num_nonnulls(target_kind, target_value, target_tolerance, units) = 0) " \
            "OR (type = 'numeric_value' AND num_nulls(target_kind, target_value) IN (0, 2)) " \
            "OR (type = 'duration' AND units IS NULL AND num_nulls(target_kind, target_value) IN (0, 2))",
            name="habit_type_shapes",
        ),
        CheckConstraint(
            "(target_kind = 'within' AND target_tolerance IS NOT NULL) " \
            "OR (target_kind != 'within' AND target_tolerance IS NULL) " \
            "OR (target_kind IS NULL AND target_tolerance IS NULL)",
            name="target_tolerance_only_exists_on_within_typed_habits",
        ),
        CheckConstraint(
            "weekly_frequency BETWEEN 1 AND 7",
            name="weekly_frequency_range"
        ),
        # null > 0 evals to unknown so we're still fine here?
        CheckConstraint("target_value > 0", name="target_positive"),
        CheckConstraint("target_tolerance > 0", name="target_tolerance_positive"),
    )

    name: Mapped[str] = mapped_column(String(HABIT_NAME_MAX_LENGTH), nullable=False)

    # Represents target completion rate per week
    weekly_frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    type: Mapped[HabitTypeEnum] = mapped_column(
        SAEnum(HabitTypeEnum, name="habit_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    # Value, kind & units for type HabitTypeEnum.NUMERIC_VALUE/DURATION
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_kind: Mapped[TargetKind | None] = mapped_column(
        SAEnum(TargetKind, name="target_kind_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    # For TargetKind.WITHIN only
    target_tolerance: Mapped[float | None] = mapped_column(Float, nullable=True)
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
        if self.target_kind is None:
            return None
        return build_target(self.target_kind, self.target_value, self.target_tolerance)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Habit id={self.id} name='{self.name}'>"


class HabitCompletion(Base):
    """Stores each completion as a new entry, enabling better analytics."""

    ## TODO: Note: "binary completions have NULL value" can't be enforced here. Service's log/toggle must do that
    __table_args__ = (
        Index("ix_habit_completions_user_habit_entry_date", "user_id", "habit_id", "entry_date"),
        UniqueConstraint("habit_id", "entry_date", name="uq_habit_completions_habit_id_entry_date"),
        CheckConstraint(
            "num_nulls(target_kind_snapshot, target_value_snapshot) IN (0, 2)",
            name="snapshot_group_all_or_nothing",
        ),
        CheckConstraint(
            "(target_kind_snapshot = 'within' AND target_tolerance_snapshot IS NOT NULL) " \
            "OR (target_kind_snapshot != 'within' AND target_tolerance_snapshot IS NULL) " \
            "OR (target_kind_snapshot IS NULL AND target_tolerance_snapshot IS NULL)",
            name="snapshot_tolerance_only_on_within",
        ),
        CheckConstraint(
            "target_kind_snapshot IS NULL OR value IS NOT NULL",
            name="snapshot_requires_value",
        ),
        CheckConstraint("value >= 0", name="value_nonnegative"),
        CheckConstraint("target_value_snapshot > 0", name="snapshot_value_positive"),
        CheckConstraint("target_tolerance_snapshot > 0", name="snapshot_tolerance_positive"),
    )

    entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_kind_snapshot: Mapped[TargetKind | None] = mapped_column(
        SAEnum(TargetKind, name="target_kind_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    target_value_snapshot: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_tolerance_snapshot: Mapped[float | None] = mapped_column(Float, nullable=True)

    habit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    habit: Mapped[Habit] = relationship("Habit", back_populates="completions")

    @property
    def target(self) -> Target | None:
        if self.target_kind_snapshot is None:
            return None
        return build_target(self.target_kind_snapshot, self.target_value_snapshot, self.target_tolerance_snapshot)

    @property
    def satisfied(self) -> bool:
        if self.target is None:
            return True
        return is_met(self.target, self.value)

    def __repr__(self) -> str:
        return f"<HabitCompletion id={self.id} habit_id={self.habit_id}>"

