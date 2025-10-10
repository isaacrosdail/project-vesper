"""
Habit service layer, to evaluate streaks & completions.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.api.responses import service_response
from app.modules.habits.constants import PROMOTION_THRESHOLD_DEFAULT
from app.modules.habits.models import StatusEnum
from app.modules.habits.repository import HabitsRepository
from app.shared.datetime.helpers import today_range_utc, last_n_days_range


class HabitsService:
    def __init__(self, repository: HabitsRepository, user_tz: str):
        self.repo = repository
        self.user_tz = user_tz

    def save_habit(self, typed_data: dict, habit_id: int | None):

        ### UPDATE
        if habit_id:
            habit = self.repo.get_habit_by_id(habit_id)
            if not habit:
                return service_response(False, "Habit not found")
            
            # Update fields
            for field, value in typed_data.items():
                setattr(habit, field, value)

            return service_response(True, "Habit updated", data={"habit": habit})

        else:
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

    # TODO: "Percent completion habits this week" - Mon to Sun
    def calculate_all_habits_percentage_this_week(self):
        # NOTE: Hardcoding 'goal amount' for now, should be a field?
        goal = 7

        # 1. Determine where we are in the week first
        today = datetime.now(ZoneInfo(self.user_tz))
        # Days since start of week
        days_elapsed = today.weekday() + 1 # offset since last_n_days_range incl today as day # 1

        # start_of_week = today - timedelta(days=today.weekday())
        start_wk_utc, eod_today_utc = last_n_days_range(days_elapsed, self.user_tz)

        # 2. Get number of completions thus far in total
        num_completions = len(self.repo.get_all_completions_in_window(start_wk_utc, eod_today_utc))

        # 3. Calc expected/"max" rate thus far into week
        habits_count = self.repo.get_count_all_habits()
        expected = (habits_count * days_elapsed)

        # 4. Percent completed thus far
        percent_completed = round((num_completions / expected) * 100, 2) if expected > 0 else 0

        return start_wk_utc, eod_today_utc, num_completions, percent_completed, habits_count