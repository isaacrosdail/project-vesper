"""
Repository layer for Habits module.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session

from sqlalchemy import func, select
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from app.modules.habits.models import (
    Habit,
    HabitCompletion,
    HabitTypeEnum,
)
from app.shared.repository.base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Habit)

    def create_habit(
        self,
        name: str,
        weekly_frequency: int,
        type: HabitTypeEnum,
        units: str | None,
        target_low: float | None,
        target_high: float | None,
    ) -> Habit:
        habit = Habit(
            user_id=self.user_id,
            name=name,
            weekly_frequency=weekly_frequency,
            type=type,
            units=units,
            target_low=target_low,
            target_high=target_high
        )
        return self.add(habit)

    def get_all_habits_and_tags(self) -> list[Habit]:
        """Return all habits, eager-loading their tags, too."""
        stmt = self._user_select(Habit).options(selectinload(Habit.tags))
        return list(self.session.scalars(stmt).all())

    def get_all_habits_and_tags_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[Habit]:
        stmt = (
            self._user_select(Habit)
            .where(
                Habit.created_at >= start_utc,
                Habit.created_at < end_utc,
            )
            .options(selectinload(Habit.tags))
        )
        return list(self.session.scalars(stmt).all())


class HabitCompletionRepository(BaseRepository[HabitCompletion]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=HabitCompletion)

    def create_habit_completion(
        self, habit_id: int, entry_date: date, *,
        value: float | None = None,
        target_low_snapshot: float | None = None,
        target_high_snapshot: float | None = None,
    ) -> HabitCompletion:
        habit_completion = HabitCompletion(
            user_id=self.user_id,
            habit_id=habit_id,
            entry_date=entry_date,
            value=value,
            target_low_snapshot=target_low_snapshot,
            target_high_snapshot=target_high_snapshot,
        )
        return self.add(habit_completion)

    def get_all_habit_completions(
        self, habit_id: int, *, order_desc: bool = False
    ) -> list[HabitCompletion]:
        stmt = self._user_select(HabitCompletion).where(
            HabitCompletion.habit_id == habit_id
        )
        if order_desc:
            stmt = stmt.order_by(HabitCompletion.entry_date.desc())
        return list(self.session.scalars(stmt).all())

    def get_in_window(
        self,
        start_date: date,
        end_date: date,
        *,
        habit_id: int | None = None
    ) -> list[HabitCompletion]:
        """Return all completions on [start_date, end_date) interval."""
        stmt = self._user_select(HabitCompletion).where(
            HabitCompletion.entry_date >= start_date,
            HabitCompletion.entry_date < end_date,
        )
        if habit_id is not None:
            stmt = stmt.where(
                HabitCompletion.habit_id == habit_id
            )
        return list(self.session.scalars(stmt).all())


    def get_completion_counts_in_window(self, start_date: date, end_date: date, habit_id: int | None = None) -> list[dict[str, Any]]:
        stmt = (
                select(HabitCompletion.entry_date.label("date"), func.count().label("count"))
                .where(
                    HabitCompletion.user_id == self.user_id,
                    HabitCompletion.entry_date >= start_date,
                    HabitCompletion.entry_date < end_date
                )
                .group_by(HabitCompletion.entry_date)
            )
        if habit_id is not None:
            stmt = stmt.where(HabitCompletion.habit_id == habit_id)
        results = self.session.execute(stmt).all()
        return [{ "date": str(row.date), "count": row.count } for row in results]


    def get_completion_counts_by_habit_in_window(
        self, start_date: date, end_date: date
    ) -> list[dict[str, str | int]]:
        """Returns a list of (habit_name, count, weekly_frequency) dicts for completions in datetime range.
        Grouped by habit name, and in descending order by completion count.
        """
        stmt = (
            select(
                Habit.name,
                func.count(HabitCompletion.id).label("completion_count"),
                Habit.weekly_frequency
            )
            .select_from(HabitCompletion)
            .join(Habit)
            .where(
                Habit.user_id == self.user_id,
                HabitCompletion.entry_date >= start_date,
                HabitCompletion.entry_date < end_date,
            )
            .group_by(Habit.name, Habit.weekly_frequency)
            .order_by(func.count(HabitCompletion.id).desc())
        )
        result = self.session.execute(stmt).all()
        return [
            {"name": row.name, "count": row.completion_count, "weekly_frequency": row.weekly_frequency }
            for row in result
        ]

    def get_completion_counts_by_week_in_window(self, habit_id: int, start_date: date, end_date: date) -> list[tuple[datetime, int]]:
        # filter by habit_id and date range, group by (week, count)
        stmt = (
            select(
                func.date_trunc("week", HabitCompletion.entry_date),
                func.count()
            )
            .where(
                HabitCompletion.user_id == self.user_id,
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.entry_date >= start_date,
                HabitCompletion.entry_date < end_date
            )
            .group_by(func.date_trunc("week", HabitCompletion.entry_date))
        )
        return list(self.session.execute(stmt).all())
