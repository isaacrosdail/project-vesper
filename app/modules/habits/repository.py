"""
Repository layer for Habits module. Remember: focus on joins/filters/paging/indexes/locking/etc.
If it touches the DB directly, it belongs here.
"""

from sqlalchemy.orm import selectinload
from datetime import datetime
from app.shared.repository.base import BaseRepository

from .models import Habit, HabitCompletion, LeetCodeRecord, StatusEnum


class HabitsRepository(BaseRepository):
    def __init__(self, session, user_id: int, user_tz: str = "UTC"):
        super().__init__(session, user_id, user_tz, model_cls=Habit)

    def get_all_habits(self):
        return self.get_all()
    
    def get_habit_by_id(self, habit_id):
        return self.get_by_id(habit_id)

    def create_habit(self, name: str, status: StatusEnum | None = None, promotion_threshold: float | None = None):
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

    # def get_all_habits_and_tags(self):
    #     return self.session.query(Habit).options(
    #         selectinload(Habit.tags) # load tags, TODO: NOTES: Prevents N+1 queries?
    #     ).filter(
    #         Habit.user_id == self.user_id
    #     ).all()
    
    
    def create_habit_completion(self, habit_id: int, created_at: datetime | None = None):
        habit_completion = HabitCompletion(
            habit_id=habit_id,
            user_id=self.user_id,
            created_at=created_at
        )
        return self.add(habit_completion)

    def get_all_habit_completions(self, habit_id: int):
        return self._user_query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id
        ).all()

    # def get_all_habit_completions(self, habit_id: int):
    #     """Return all completions for the given habit, scoped to current user."""
    #     return self.session.query(HabitCompletion).join(Habit).filter(
    #         HabitCompletion.habit_id == habit_id,
    #         Habit.user_id == self.user_id,
    #     ).all()
    
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
        return self.add(new_record)

    # TODO
    def get_all_leetcoderecords_in_window(self, start_utc, end_utc) -> list[LeetCodeRecord]:
        return self.session.query(LeetCodeRecord).filter(
            LeetCodeRecord.created_at >= start_utc,
            LeetCodeRecord.created_at < end_utc
        ).all()