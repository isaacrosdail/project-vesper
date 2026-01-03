"""
Habit service layer, to evaluate streaks & completions.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from datetime import datetime
from zoneinfo import ZoneInfo

from app.api.responses import service_response
from app.modules.habits.models import StatusEnum
from app.modules.habits.repository import HabitRepository, HabitCompletionRepository, LeetCodeRecordRepository
from app.shared.datetime.helpers import today_range_utc, last_n_days_range


class HabitsService:
    def __init__(
    self,
        session: 'Session',
        user_tz: str,
        habit_repo: HabitRepository, 
        completion_repo: HabitCompletionRepository, 
        leetcode_repo: LeetCodeRecordRepository,
    ):
        self.session = session
        self.user_tz = user_tz
        self.habit_repo = habit_repo
        self.completion_repo = completion_repo
        self.leetcode_repo = leetcode_repo

    def save_habit(self, typed_data: dict[str, Any], habit_id: int | None) -> Any:

        ### UPDATE
        if habit_id:
            habit = self.habit_repo.get_by_id(habit_id)
            if not habit:
                return service_response(False, "Habit not found")
            
            # Update fields
            for field, value in typed_data.items():
                setattr(habit, field, value)

            return service_response(True, "Habit updated", data={"habit": habit})

        else:
            habit = self.habit_repo.create_habit(
                name=typed_data["name"],
                status=typed_data.get("status"),
                promotion_threshold=typed_data.get("promotion_threshold"),
                target_frequency=typed_data["target_frequency"]
            )
            return service_response(True, "Habit added", data={"habit": habit})


    ### TODO: Performance - N+1 query issue for dashboard, batch/cache?
    def calculate_habit_streak(self, habit_id: int) -> int:
        """Calculate current streak for given habit."""
        habit_completions = self.completion_repo.get_all_habit_completions(habit_id, order_desc=True)

        if not habit_completions:
            return 0
        
        # Convert to user timezone for calendar day logic
        # local_completion_dates => list of dates of completions only, in user's timezone
        user_timezone = ZoneInfo(self.user_tz)
        today_date = datetime.now(user_timezone).date()
        local_completion_dates = [c.created_at.astimezone(user_timezone).date() for c in habit_completions]

        # Check if streak exists (within 2 days of most recent)
        if (today_date - local_completion_dates[0]).days < 2:
            streak = 1
            for i in range(len(local_completion_dates) - 1): # Remember: -1 here to avoid out of bounds!
                if (local_completion_dates[i] - local_completion_dates[i+1]).days == 1:
                    streak += 1
                else:
                    break # gap found, streak ends here!
            return streak
        else:
            return 0

    def check_if_completed_today(self, habit_id: int) -> bool:
        """
        Return True if the user completed the given habit today (according to local timezone).
        """
        start_utc, end_utc = today_range_utc(self.user_tz)
        completion = self.completion_repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
        return completion is not None

    # TODO: "Percent completion habits this week" - Mon to Sun
    def calculate_all_habits_percentage_this_week(self) -> dict[str, Any]:
        # Determine current day in the week
        today = datetime.now(ZoneInfo(self.user_tz))
        days_into_week = today.weekday() + 1 # offset: incl today as day # 1

        # start_of_week = today - timedelta(days=today.weekday())
        start_of_week_utc, end_of_today_utc = last_n_days_range(days_into_week, self.user_tz)

        # Fetch completions in that time range
        total_completions = len(self.completion_repo.get_all_completions_in_window(start_of_week_utc, end_of_today_utc))

        # Expected_completions is sum of target_frequency for all
        habits = self.habit_repo.get_all_habits_and_tags()
        expected_completions = sum(h.target_frequency or 0 for h in habits)

        # Calculate completion percentage
        percent_completed = round((total_completions / expected_completions) * 100, 2) if expected_completions > 0 else 0

        return {
            "completed": total_completions,
            "total": expected_completions,
            "percent": percent_completed
        }
    
def create_habits_service(session: 'Session', user_id: int, user_tz: str) -> HabitsService:
    """Factory function to instantiate HabitsService with required repositories."""
    return HabitsService(
        session=session,
        user_tz=user_tz,
        habit_repo=HabitRepository(session, user_id),
        completion_repo=HabitCompletionRepository(session, user_id),
        leetcode_repo=LeetCodeRecordRepository(session, user_id),
    )