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
from sqlalchemy.orm import InstrumentedAttribute

from app.modules.habits.models import (
    Habit,
    HabitCompletion,
    HabitTypeEnum,
    ScheduleTypeEnum,
)
from app.shared.repository.base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Habit)

    def create_habit(
        self,
        name: str,
        type: HabitTypeEnum,
        schedule_type: ScheduleTypeEnum,
        start_date: date,
        *,
        weekly_frequency: int | None = None,
        scheduled_days: list[int] | None = None,
        monthly_days: list[int] | None = None,
        interval_days: int | None = None,
        end_date: date | None = None,
        units: str | None = None,
        target_low: float | None = None,
        target_high: float | None = None,
    ) -> Habit:
        habit = Habit(
            user_id=self.user_id,
            name=name,
            type=type,
            schedule_type=schedule_type,
            start_date=start_date,
            end_date=end_date,
            weekly_frequency=weekly_frequency,
            scheduled_days=scheduled_days,
            monthly_days=monthly_days,
            interval_days=interval_days,
            units=units,
            target_low=target_low,
            target_high=target_high
        )
        return self.add(habit)


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
    ) -> dict[int, int]:
        """Completion counts per habit on [start_date, end_date)."""
        stmt = (
            select(HabitCompletion.habit_id, func.count().label("count"))
            .where(
                HabitCompletion.user_id == self.user_id,
                HabitCompletion.entry_date >= start_date,
                HabitCompletion.entry_date < end_date,
            )
            .group_by(HabitCompletion.habit_id)
        )
        return {habit_id: n for habit_id, n in self.session.execute(stmt)}

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
        return [(week, n) for week, n in self.session.execute(stmt)]
