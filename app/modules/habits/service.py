"""
Habit service layer, to evaluate streaks & completions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import date
    from sqlalchemy.orm import Session


from datetime import datetime
from itertools import pairwise
from zoneinfo import ZoneInfo

import pandas as pd

import app.shared.datetime_.helpers as dth
from app.api.responses import service_response
from app.modules.habits.repository import (
    HabitCompletionRepository,
    HabitRepository,
    LeetCodeRecordRepository,
)

STREAK_GRACE_DAYS = 2  # Allow yesterday or today to continue streak


class HabitsService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        habit_repo: HabitRepository,
        completion_repo: HabitCompletionRepository,
        leetcode_repo: LeetCodeRecordRepository,
    ) -> None:
        self.session = session
        self.user_tz = user_tz
        self.habit_repo = habit_repo
        self.completion_repo = completion_repo
        self.leetcode_repo = leetcode_repo

    def save_habit(self, typed_data: dict[str, Any], habit_id: int | None) -> Any:
        # UPDATE
        if habit_id:
            habit = self.habit_repo.get_by_id(habit_id)
            if not habit:
                return service_response(success=False, message="Habit not found")

            for field, value in typed_data.items():
                setattr(habit, field, value)

            return service_response(
                success=True, message="Habit updated", data={"habit": habit}
            )

        else:
            habit = self.habit_repo.create_habit(
                name=typed_data["name"],
                status=typed_data.get("status"),
                promotion_threshold=typed_data.get("promotion_threshold"),
                target_frequency=typed_data["target_frequency"],
            )
            return service_response(
                success=True, message="Habit added", data={"habit": habit}
            )

    # Streak calc: scan completion dates looking for consecutive days
    #  Similar pattern to LC#121 (Best Time to Buy/Sell Stock) - one-pass scan with invariant
    # prices[i] <-> completion_dates[i]
    # min_price <-> anchor date (most recent valid completion)
    # max_profit <-> streak length
    def calculate_habit_streak(self, habit_id: int) -> int:
        """Calculate current streak for given habit."""
        habit_completions = self.completion_repo.get_all_habit_completions(
            habit_id, order_desc=True
        )

        if not habit_completions:
            return 0

        # Convert to user timezone for calendar day logic
        user_timezone = ZoneInfo(self.user_tz)
        today_date = datetime.now(user_timezone).date()
        local_completion_dates = [
            c.created_at.astimezone(user_timezone).date() for c in habit_completions
        ]

        # Check if streak exists (must be within 2 days of today)
        if (today_date - local_completion_dates[0]).days >= STREAK_GRACE_DAYS:
            return 0

        # Count consecutive days using pairwise()
        # pairwise() = lazy iterator, no list allocation: O(n) time, O(1) extra space
        # Stil O(n) like zip(seq, seq[1:]) would be
        streak = 1
        for curr_date, prev_date in pairwise(local_completion_dates):
            if (curr_date - prev_date).days == 1:
                streak += 1
            else:
                break

        return streak


    def check_if_completed_today(self, habit_id: int) -> bool:
        """
        Return True if the user completed the given habit today (according to local timezone).
        """
        start_utc, end_utc = dth.today_range_utc(self.user_tz)
        completion = self.completion_repo.get_habit_completion_in_window(
            habit_id, start_utc, end_utc
        )
        return completion is not None

    # NOTE: "Percent completion habits this week" - Mon to Sun
    def calculate_all_habits_percentage_this_week(self) -> dict[str, Any]:
        """
        Calculate aggregate habit completion progress for the current week.

        Computes total number of recorded habit completions from Mon. through today (inclusive), the
        total expected completions based on each habit's target frequency, and the resulting completion percentage.
        """
        # Determine current day in the week
        today = datetime.now(ZoneInfo(self.user_tz))
        days_into_week = today.weekday() + 1  # offset: incl today as day # 1

        # start_of_week = today - timedelta(days=today.weekday())
        start_of_week_utc, end_of_today_utc = dth.last_n_days_range(
            days_into_week, self.user_tz
        )

        # Fetch completions in that time range
        total_completions = len(
            self.completion_repo.get_all_completions_in_window(
                start_of_week_utc, end_of_today_utc
            )
        )

        # Expected_completions is sum of target_frequency for all
        habits = self.habit_repo.get_all_habits_and_tags()
        expected_completions = sum(h.target_frequency or 0 for h in habits)

        # Calculate completion percentage
        percent_completed = (
            round((total_completions / expected_completions) * 100, 2)
            if expected_completions > 0
            else 0
        )

        return {
            "completed": total_completions,
            "total": expected_completions,
            "percent": percent_completed,
        }
    
    def get_daily_completion_counts(self) -> pd.DataFrame:
        # fetches all completion records for user
        completion_records = self.completion_repo.get_all()

        # convert each created_at to local date, so we'll just have
        # a list of completion counts per date
        completion_records_local = [
            dth.convert_to_timezone(self.user_tz, entry.created_at).date()
            for entry in completion_records
        ]
        import sys
        print(completion_records_local, file=sys.stderr)

        # group by local date + count completions per day

        # creating dataframe from a list:
        df = pd.DataFrame({ "date": completion_records_local })
        print(df, file=sys.stderr)

        # count occurrences of each val in a col:
        # groupby("date") groups rows by unique date values
        # size() counts how many rows are in each group
        # .reset_index(name="completion_count") turns it back into a clean two-col DataFrame:
        # date and completion_count
        df = df.groupby("date").size().reset_index(name="completion_count")
        print(df, file=sys.stderr)

        return df


def create_habits_service(
    session: Session, user_id: int, user_tz: str
) -> HabitsService:
    """Factory function to instantiate HabitsService with required repositories."""
    return HabitsService(
        session=session,
        user_tz=user_tz,
        habit_repo=HabitRepository(session, user_id),
        completion_repo=HabitCompletionRepository(session, user_id),
        leetcode_repo=LeetCodeRecordRepository(session, user_id),
    )
