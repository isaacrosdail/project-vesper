"""
Habit service layer, to evaluate streaks & completions.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.api.responses import service_response
from app.modules.habits.constants import PROMOTION_THRESHOLD_DEFAULT
from app.modules.habits.models import StatusEnum
from app.modules.habits.repository import HabitsRepository
from app.shared.datetime.helpers import today_range_utc


class HabitsService:
    def __init__(self, repository: HabitsRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def create_habit(self, typed_data: dict):
        
        # Promotion-based habits
        if typed_data.get("is_promotable"):
            typed_data["status"] = StatusEnum.EXPERIMENTAL
            typed_data["promotion_threshold"] = PROMOTION_THRESHOLD_DEFAULT

        habit = self.repo.create_habit(
            name=typed_data["name"],
            status=typed_data.get("status"),
            promotion_threshold=typed_data.get("promotion_threshold")
        )
        return service_response(True, "Habit added", data={"habit": habit})


    ### TODO: Performance - N+1 query issue for dashboard, batch/cache?
    def calculate_habit_streak(self, habit_id: int) -> int:
        """Calculate current streak for given habit."""
        habit_completions = self.repo.get_all_habit_completions_descending(habit_id)

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
        completion = self.repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
        return completion is not None

