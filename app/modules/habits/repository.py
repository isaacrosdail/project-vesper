"""
Repository layer for Habits module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.modules.habits.models import (
    DifficultyEnum,
    Habit,
    HabitCompletion,
    LanguageEnum,
    LCStatusEnum,
    LeetCodeRecord,
    StatusEnum,
)
from app.shared.models import Pillar
from app.shared.repository.base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=Habit)

    def create_habit(
        self,
        name: str,
        status: StatusEnum | None,
        target_frequency: int,
        pillar_ids: list[int] | None = None
    ) -> Habit:
        habit = Habit(
            user_id=self.user_id,
            name=name,
            status=status,
            target_frequency=target_frequency,
        )
        # TODO: fixup
        if pillar_ids:
            stmt = select(Pillar).where(
                Pillar.id.in_(pillar_ids),
                Pillar.user_id == self.user_id
            )
            result = list(self.session.scalars(stmt).all())
            habit.pillars = result
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
        self, habit_id: int, completed_at: datetime
    ) -> HabitCompletion:
        habit_completion = HabitCompletion(
            user_id=self.user_id,
            habit_id=habit_id,
            completed_at=completed_at
        )
        return self.add(habit_completion)

    def get_all_habit_completions(
        self, habit_id: int, *, order_desc: bool = False
    ) -> list[HabitCompletion]:
        stmt = self._user_select(HabitCompletion).where(
            HabitCompletion.habit_id == habit_id
        )
        if order_desc:
            stmt = stmt.order_by(HabitCompletion.completed_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_habit_completion_in_window(
        self, habit_id: int, start_utc: datetime, end_utc: datetime
    ) -> HabitCompletion | None:
        """Return HabitCompletion for a given habit on a given day, scoped to current user."""
        stmt = (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.completed_at >= start_utc,
                HabitCompletion.completed_at < end_utc,
                Habit.user_id == self.user_id,
            )
        )
        return self.session.scalars(stmt).first()

    def get_completion_counts_in_window(self, start_utc: datetime, end_utc: datetime) -> list[dict[str, Any]]:
        stmt = (
                select(func.date(HabitCompletion.completed_at).label("date"), func.count().label("count"))
                .where(
                    HabitCompletion.user_id == self.user_id,
                    HabitCompletion.completed_at >= start_utc,
                    HabitCompletion.completed_at < end_utc
                )
                .group_by(func.date(HabitCompletion.completed_at))
            )
        results = self.session.execute(stmt).all()
        return [{ "date": str(row.date), "count": row.count } for row in results]

    ## All for a given habit
    def get_all_single_habit_completions_in_window(
        self, habit_id: int, start_utc: datetime, end_utc: datetime
    ) -> list[HabitCompletion]:
        stmt = (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(
                Habit.id == habit_id,
                Habit.user_id == self.user_id,
                HabitCompletion.completed_at >= start_utc,
                HabitCompletion.completed_at < end_utc,
            )
        )
        return list(self.session.scalars(stmt).all())

    ## ALL habits in general
    ## TODO: Even necessary? or should use the generic in window now?
    def get_all_completions_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[HabitCompletion]:
        # stmt = (
        #     select(HabitCompletion)
        #     .join(Habit, Habit.id == HabitCompletion.habit_id) # TODO: stupid join?
        #     .where(
        #         Habit.user_id == self.user_id,
        #         HabitCompletion.created_at >= start_utc,
        #         HabitCompletion.created_at < end_utc,
        #     )
        # )
        stmt = self._user_select(HabitCompletion).where(
            HabitCompletion.completed_at >= start_utc,
            HabitCompletion.completed_at < end_utc,
        )
        return list(self.session.scalars(stmt).all())

    def get_completion_counts_by_habit_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[dict[str, str | int]]:
        """Returns a list of (habit_name, count, target_frequency) dicts for completions in datetime range.
        Grouped by habit name, and in descending order by completion count.
        """
        stmt = (
            select(
                Habit.name,
                func.count(HabitCompletion.id).label("completion_count"),
                Habit.target_frequency
            )
            .select_from(HabitCompletion)
            .join(Habit)
            .where(
                Habit.user_id == self.user_id,
                HabitCompletion.completed_at >= start_utc,
                HabitCompletion.completed_at < end_utc,
            )
            .group_by(Habit.name, Habit.target_frequency)
            .order_by(func.count(HabitCompletion.id).desc())
        )
        result = self.session.execute(stmt).all()
        return [
            {"name": row.name, "count": row.completion_count, "target_frequency": row.target_frequency }
            for row in result
        ]  # unwrap each SQLAlchemy Row into a list of dicts

    def get_completion_counts_by_week_in_window(self, habit_id: int, start_utc: datetime, end_utc: datetime) -> list[tuple[int, int]]:
        # filter by habit_id and date range, group by (week, count)
        stmt = (
            select(
                func.extract("week", HabitCompletion.completed_at),
                func.count()
            )
            .where(
                HabitCompletion.user_id == self.user_id,
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.completed_at >= start_utc,
                HabitCompletion.completed_at < end_utc
            )
            .group_by(func.extract("week", HabitCompletion.completed_at))
        )
        return list(self.session.execute(stmt).all())


class LeetCodeRecordRepository(BaseRepository[LeetCodeRecord]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=LeetCodeRecord)

    def create_leetcoderecord(
        self,
        leetcode_id: int,
        difficulty: DifficultyEnum,
        language: LanguageEnum,
        status: LCStatusEnum,
        title: str | None,
    ) -> LeetCodeRecord:
        new_record = LeetCodeRecord(
            user_id=self.user_id,
            leetcode_id=leetcode_id,
            title=title,
            difficulty=difficulty,
            language=language,
            status=status,
        )
        return self.add(new_record)
