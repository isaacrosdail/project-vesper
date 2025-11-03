"""
Repository layer for Habits module.
"""

from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.modules.habits.models import Habit, HabitCompletion, LeetCodeRecord, StatusEnum, DifficultyEnum, LanguageEnum, LCStatusEnum
from app.shared.repository.base import BaseRepository


class HabitsRepository(BaseRepository):
    def __init__(self, session, user_id: int, user_tz: str = "UTC"):
        super().__init__(session, user_id, user_tz, model_cls=Habit)

    def create_habit(self, name: str, status: StatusEnum | None, promotion_threshold: float | None):
        habit = Habit(
            user_id=self.user_id,
            name=name,
            status=status,
            promotion_threshold=promotion_threshold
        )
        return self.add(habit)

    def get_all_habits_and_tags(self):
        """Return all habits, eager-loading their tags, too."""
        stmt = self._user_select(Habit).options(
            selectinload(Habit.tags)
        )
        return self.session.execute(stmt).scalars().all()

    def create_habit_completion(self, habit_id: int, created_at: datetime):
        habit_completion = HabitCompletion(
            user_id=self.user_id,
            habit_id=habit_id,
            created_at=created_at
        )
        return self.add(habit_completion)

    def get_all_habit_completions(self, habit_id: int, order_desc: bool = False):
        stmt = self._user_select(HabitCompletion).where(
            HabitCompletion.habit_id == habit_id
        )
        if order_desc:
            stmt = stmt.order_by(HabitCompletion.created_at.desc())
        return self.session.execute(stmt).scalars().all()

    def get_habit_completion_in_window(self, habit_id: int, start_utc: datetime, end_utc: datetime):
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
    def get_all_single_habit_completions_in_window(self, habit_id: int, start_utc: datetime, end_utc: datetime):
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
        return self.session.execute(stmt).scalars().all()

    ## ALL habits in general
    def get_all_completions_in_window(self, start_utc: datetime, end_utc: datetime):
        stmt = (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(
                Habit.user_id == self.user_id,
                HabitCompletion.created_at >= start_utc,
                HabitCompletion.created_at < end_utc
            )
        )
        return self.session.execute(stmt).scalars().all()
    
    def get_completion_counts_by_habit_in_window(self, start_utc: datetime, end_utc: datetime):
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
        return self.session.execute(stmt).all()

    def create_leetcoderecord(self, leetcode_id: int, difficulty: DifficultyEnum,
                              language: LanguageEnum, status: LCStatusEnum,
                              title: str | None) -> LeetCodeRecord:
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
        return self.session.execute(stmt).scalars().all()
