"""
Repository layer for Habits module.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.modules.habits.models import (DifficultyEnum, Habit, HabitCompletion,
                                       LanguageEnum, LCStatusEnum,
                                       LeetCodeRecord, StatusEnum)
from app.shared.repository.base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    def __init__(self, session: 'Session', user_id: int):
        super().__init__(session, user_id, model_cls=Habit)

    def create_habit(
            self,
            name: str,
            status: StatusEnum | None,
            promotion_threshold: float | None,
            target_frequency: int
    ) -> Habit:
        habit = Habit(
            user_id=self.user_id,
            name=name,
            status=status,
            promotion_threshold=promotion_threshold,
            target_frequency=target_frequency
        )
        return self.add(habit)

    def get_all_habits_and_tags(self) -> list[Habit]:
        """Return all habits, eager-loading their tags, too."""
        stmt = self._user_select(Habit).options(
            selectinload(Habit.tags)
        )
        return list(self.session.execute(stmt).scalars().all())
    
    def get_all_habits_and_tags_in_window(self, start_utc: datetime, end_utc: datetime) -> list[Habit]:
        stmt = self._user_select(Habit).where(
            Habit.created_at >= start_utc,
            Habit.created_at < end_utc,
        ).options(
            selectinload(Habit.tags)
        )
        return list(self.session.execute(stmt).scalars().all())


class HabitCompletionRepository(BaseRepository[HabitCompletion]):
    def __init__(self, session: 'Session', user_id: int):
        super().__init__(session, user_id, model_cls=HabitCompletion)


    def create_habit_completion(self, habit_id: int, created_at: datetime) -> HabitCompletion:
        habit_completion = HabitCompletion(
            user_id=self.user_id,
            habit_id=habit_id,
            created_at=created_at
        )
        return self.add(habit_completion)

    def get_all_habit_completions(self, habit_id: int, order_desc: bool = False) -> list[HabitCompletion]:
        stmt = self._user_select(HabitCompletion).where(
            HabitCompletion.habit_id == habit_id
        )
        if order_desc:
            stmt = stmt.order_by(HabitCompletion.created_at.desc())
        return list(self.session.execute(stmt).scalars().all())

    def get_habit_completion_in_window(self, habit_id: int, start_utc: datetime, end_utc: datetime) -> HabitCompletion | None:
        """Return HabitCompletion for a given habit on a given day, scoped to current user."""
        stmt = (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(
                HabitCompletion.habit_id == habit_id,
                HabitCompletion.created_at >= start_utc,
                HabitCompletion.created_at < end_utc,
                Habit.user_id == self.user_id,
            )
        )
        return self.session.execute(stmt).scalars().first()

    ## All for a given habit
    def get_all_single_habit_completions_in_window(self, habit_id: int, start_utc: datetime, end_utc: datetime) -> list[HabitCompletion]:
        stmt = (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(
                Habit.id == habit_id,
                Habit.user_id == self.user_id,
                HabitCompletion.created_at >= start_utc,
                HabitCompletion.created_at < end_utc
            )
        )
        return list(self.session.execute(stmt).scalars().all())

    ## ALL habits in general
    def get_all_completions_in_window(self, start_utc: datetime, end_utc: datetime) -> list[HabitCompletion]:
        stmt = (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(
                Habit.user_id == self.user_id,
                HabitCompletion.created_at >= start_utc,
                HabitCompletion.created_at < end_utc
            )
        )
        return list(self.session.execute(stmt).scalars().all())
    
    def get_completion_counts_by_habit_in_window(self, start_utc: datetime, end_utc: datetime) -> list[tuple[str, int]]:
        """Returns a list of (habit_name, count) tuples for completions in datetime range."""
        stmt = (
            select(Habit.name, func.count(HabitCompletion.id))
            .select_from(HabitCompletion)
            .join(Habit)
            .where(
                Habit.user_id == self.user_id,
                HabitCompletion.created_at >= start_utc,
                HabitCompletion.created_at < end_utc
            )
            .group_by(Habit.name)
        )
        result = self.session.execute(stmt).all()
        return [tuple(row) for row in result] # unwrap each SQLAlchemy Row into a plain tuple


class LeetCodeRecordRepository(BaseRepository[LeetCodeRecord]):
    def __init__(self, session: 'Session', user_id: int):
        super().__init__(session, user_id, model_cls=LeetCodeRecord)


    def create_leetcoderecord(
            self,
            leetcode_id: int,
            difficulty: DifficultyEnum,
            language: LanguageEnum,
            status: LCStatusEnum,
            title: str | None
    ) -> LeetCodeRecord:
        new_record = LeetCodeRecord(
            user_id=self.user_id,
            leetcode_id=leetcode_id,
            title=title,
            difficulty=difficulty, # Note: can pass the enum member itself, no need for .value
            language=language,
            status=status
        )
        return self.add(new_record)

    def get_all_leetcoderecords_in_window(self, start_utc: datetime, end_utc: datetime) -> list[LeetCodeRecord]:
        stmt = self._user_select(LeetCodeRecord).where(
            LeetCodeRecord.created_at >= start_utc,
            LeetCodeRecord.created_at < end_utc
        )
        return list(self.session.execute(stmt).scalars().all())