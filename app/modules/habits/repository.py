"""
Repository layer for Habits module. Remember: focus on joins/filters/paging/indexes/locking/etc.
If it touches the DB directly, it belongs here.
"""

from sqlalchemy.orm import selectinload
from datetime import datetime
from app.shared.repository.base import BaseRepository

from .models import Habit, HabitCompletion, LeetCodeRecord


class HabitsRepository(BaseRepository):

    # Get all habits for current user id
    def get_all_habits(self):
        """Return all habits scoped to current user."""
        return self.session.query(Habit).filter(
            Habit.user_id == self.user_id
        ).all()
    
    def get_all_habits_and_tags(self):
        """Return all habits, eager-loading their tags too."""
        return self.session.query(Habit).options(
            selectinload(Habit.tags) # load tags, TODO: NOTES: Prevents N+1 queries?
        ).filter(
            Habit.user_id == self.user_id
        ).all()
    
    def create_habit(self, name: str):
        habit = Habit(
            user_id=self.user_id,
            name=name
        )
        self.session.add(habit)
        self.session.flush()
        return habit
    
    def create_habit_completion(self, habit_id: int, created_at: datetime | None = None):
        habit_completion = HabitCompletion(
            habit_id=habit_id,
            user_id=self.user_id,
            created_at=created_at
        )
        self.session.add(habit_completion)
        return habit_completion

    def get_habit_by_id(self, habit_id: int):
        """Return a single habit by its ID."""
        return self.session.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == self.user_id
        ).first()

    def get_all_habit_completions(self, habit_id: int):
        """Return all completions for the given habit, scoped to current user."""
        return self.session.query(HabitCompletion).join(Habit).filter(
            HabitCompletion.habit_id == habit_id,
            Habit.user_id == self.user_id,
        ).all()
    
    def get_all_habit_completions_descending(self, habit_id: int):
        """Return all HabitCompletions for given habit, most recent first."""
        return (
            self.session.query(HabitCompletion)
            .filter(HabitCompletion.habit_id == habit_id)
            .order_by(HabitCompletion.created_at.desc())
            .all()
        )

    def get_habit_completion_in_window(self, habit_id: int, start_utc, end_utc):
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
    
    def create_leetcoderecord(self, leetcode_id: int, difficulty, language, lcstatus, title: str | None = None):
        new_record = LeetCodeRecord(
            user_id=self.user_id,
            leetcode_id=leetcode_id,
            title=title,
            difficulty=difficulty, # Note: can pass the enum member itself, no need for .value
            language=language,
            status=lcstatus
        )
        self.session.add(new_record)
        self.session.flush()
        return new_record
    
    def get_all_leetcoderecords_in_window(self, start_utc, end_utc) -> list[LeetCodeRecord]:
        return self.session.query(LeetCodeRecord).filter(
            LeetCodeRecord.created_at >= start_utc,
            LeetCodeRecord.created_at < end_utc
        ).all()