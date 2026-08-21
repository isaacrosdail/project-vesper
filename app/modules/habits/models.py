"""
Model definitions for Habits module.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum, auto
from itertools import takewhile

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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.models import Pillar, Tag, habit_pillars, habit_tags
from app.shared.target import Target

HABIT_NAME_MAX_LENGTH = 100

class HabitTypeEnum(StrEnum):
    BINARY = auto()
    NUMERIC_VALUE = auto()
    DURATION = auto()


class ScheduleTypeEnum(StrEnum):
    FREQUENCY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    INTERVAL = auto()


class DatedSchedule:
    __slots__ = ()

    def intended_dates(self, start: date, end: date) -> Iterator[date]:
        raise NotImplementedError

    def intended_in_window(self, start_date: date, window_start: date, window_end: date) -> set[date]:
        return set(takewhile(lambda d: d >= window_start, self.intended_dates(start_date, window_end)))

@dataclass(frozen=True, slots=True)
class WeeklySchedule(DatedSchedule):
    scheduled_days: list[int]

    def intended_dates(self, start: date, end: date) -> Iterator[date]:
        d = end
        while d >= start:
            if d.isoweekday() in self.scheduled_days:
                yield d
            d -= timedelta(days=1)

@dataclass(frozen=True, slots=True)
class IntervalSchedule(DatedSchedule):
    interval_days: int

    def intended_dates(self, start: date, end: date) -> Iterator[date]:
        # Snap down to most recent interval'd date, walk back from there
        remainder = (end - start).days % self.interval_days
        snapped_date = end - timedelta(days=remainder)
        d = snapped_date
        while d >= start:
            yield d
            d -= timedelta(days=self.interval_days)

@dataclass(frozen=True, slots=True)
class MonthlySchedule(DatedSchedule):
    monthly_days: list[int]

    def intended_dates(self, start: date, end: date) -> Iterator[date]:
        d = end
        while d >= start:
            if (d.day in self.monthly_days) or (-1 in self.monthly_days and (d + timedelta(days=1)).day == 1):
                yield d
            d -= timedelta(days=1)

@dataclass(frozen=True, slots=True)
class FrequencySchedule:
    weekly_frequency: int

Schedule = WeeklySchedule | IntervalSchedule | MonthlySchedule | FrequencySchedule

def _required[T](val: T | None, field: str) -> T:
    if val is None:
        raise ValueError(f"habit missing {field} for its schedule_type")
    return val

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
        CheckConstraint("end_date >= start_date", name="end_date_after_start_date"),
        CheckConstraint(
            "num_nonnulls(weekly_frequency, scheduled_days, monthly_days, interval_days) = 1 "
            "AND ((schedule_type = 'frequency' AND weekly_frequency IS NOT NULL) "
            "OR (schedule_type = 'weekly' AND scheduled_days IS NOT NULL) "
            "OR (schedule_type = 'monthly' AND monthly_days IS NOT NULL) "
            "OR (schedule_type = 'interval' AND interval_days IS NOT NULL))",
            name="schedule_shapes",
        ),
    )

    name: Mapped[str] = mapped_column(String(HABIT_NAME_MAX_LENGTH), nullable=False)

    # Default to user's today in service if not given
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    schedule_type: Mapped[ScheduleTypeEnum] = mapped_column(
        SAEnum(ScheduleTypeEnum, name="schedule_type_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    scheduled_days: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    monthly_days: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    weekly_frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

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
    def schedule(self) -> Schedule:
        match self.schedule_type:
            case ScheduleTypeEnum.INTERVAL:
                return IntervalSchedule(interval_days=_required(self.interval_days, "interval_days"))
            case ScheduleTypeEnum.WEEKLY:
                return WeeklySchedule(scheduled_days=_required(self.scheduled_days, "scheduled_days"))
            case ScheduleTypeEnum.MONTHLY:
                return MonthlySchedule(monthly_days=_required(self.monthly_days, "monthly_days"))
            case ScheduleTypeEnum.FREQUENCY:
                return FrequencySchedule(weekly_frequency=_required(self.weekly_frequency, "weekly_frequency"))

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

