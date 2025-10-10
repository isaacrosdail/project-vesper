"""
Repository layer for Habits module.
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.modules.habits.models import Habit, HabitCompletion, LeetCodeRecord, StatusEnum, DifficultyEnum, LanguageEnum, LCStatusEnum
from app.shared.repository.base import BaseRepository


class HabitsRepository(BaseRepository):
    def __init__(self, session, user_id: int, user_tz: str = "UTC"):
        super().__init__(session, user_id, user_tz, model_cls=Habit)

    def get_all_habits(self):
        return self.get_all()
    
    def get_count_all_habits(self):
        return self.get_count_all()
    
    def get_habit_by_id(self, habit_id: int):
        return self.get_by_id(habit_id)

    def create_habit(self, name: str, status: StatusEnum | None, promotion_threshold: float | None):
        habit = Habit(
            user_id=self.user_id,
            name=name,
            status=status,
            promotion_threshold=promotion_threshold
        )
        return self.add(habit)
    
    def get_all_habits_and_tags(self):
        """Return all habits, eager-loading their tags too."""
        return self._user_query(Habit).options(
            selectinload(Habit.tags)
        ).all()


    def create_habit_completion(self, habit_id: int, created_at: datetime):
        habit_completion = HabitCompletion(
            user_id=self.user_id,
            habit_id=habit_id,
            created_at=created_at
        )
        return self.add(habit_completion)

    def get_all_habit_completions(self, habit_id: int):
        return self._user_query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id
        ).all()


    # TODO
    def get_all_habit_completions_descending(self, habit_id: int):
        """Return all HabitCompletions for given habit, most recent first."""
        return (
            self.session.query(HabitCompletion)
            .filter(HabitCompletion.habit_id == habit_id)
            .order_by(HabitCompletion.created_at.desc())
            .all()
        )

    # TODO
    def get_habit_completion_in_window(self, habit_id: int, start_utc: datetime, end_utc: datetime):
        """Return HabitCompletion for a given habit on a given day, scoped to current user."""
        return (
            self.session.query(HabitCompletion)
            .join(Habit)
            .filter(
                HabitCompletion.habit_id == habit_id,
                Habit.user_id == self.user_id,
                HabitCompletion.created_at >= start_utc,
                HabitCompletion.created_at < end_utc
            )
            .first()
        )
    
    ## All for a given habit
    def get_all_single_habit_completions_in_window(self, habit_id: int, start_utc, end_utc):
        return self._user_query(HabitCompletion).join(Habit).filter(
            Habit.id == habit_id,
            HabitCompletion.created_at >= start_utc,
            HabitCompletion.created_at < end_utc
        ).all()

    ## ALL habits in general
    def get_all_completions_in_window(self, start_utc, end_utc):
        return self._user_query(HabitCompletion).join(Habit).filter(
            HabitCompletion.created_at >= start_utc,
            HabitCompletion.created_at < end_utc
        ).all()
    
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

    # TODO
    def get_all_leetcoderecords_in_window(self, start_utc: datetime, end_utc: datetime) -> list[LeetCodeRecord]:
        return self._user_query(LeetCodeRecord).filter(
            LeetCodeRecord.created_at >= start_utc,
            LeetCodeRecord.created_at < end_utc
        ).all()