"""
Habit service layer, to evaluate streaks & completions.
"""
# TODO: Implement habit promotion logic.
from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.habits.repository import HabitsRepository
from app.shared.datetime.helpers import today_range


def calculate_habit_streak(session, user_id: int, habit_id: int, user_tz: str) -> int:
    """Calculate current streak for given habit."""
    repo = HabitsRepository(session, user_id, user_tz)
    habit_completions = repo.get_all_habit_completions_descending(habit_id)

    if not habit_completions:
        return 0
    
    # Convert to user timezone for calendar day logic
    # local_completion_dates => list of dates of completions only, in user's timezone
    user_timezone = ZoneInfo(user_tz)
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

def check_if_completed_today(session, user_id, habit_id: int, user_tz: str):
    """
    Return True if the user completed the given habit today (according to local timezone).
    """
    start_utc, end_utc = today_range(user_tz)
    repo = HabitsRepository(session, user_id, user_tz)
    completion = repo.get_habit_completion_in_window(habit_id, start_utc, end_utc)
    return completion is not None