"""
Habit service layer, to evaluate streaks & completions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.habits.models import Habit, HabitCompletion
    from app.modules.habits.schemas import HabitCreate
    from app.modules.habits.schemas import HabitPatch as HabitUpdate

from collections import defaultdict
from datetime import date, datetime, timedelta
from itertools import pairwise
from zoneinfo import ZoneInfo

import pandas as pd

import app.shared.datetime_.helpers as dth
from app.modules.habits.models import PROMOTION_THRESHOLD, StatusEnum
from app.modules.habits.repository import (
    HabitCompletionRepository,
    HabitRepository,
)
from app.shared.exceptions import ServiceError
from app.shared.repository.pillar import PillarRepository


class HabitsService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        habit_repo: HabitRepository,
        completion_repo: HabitCompletionRepository,
        pillar_repo: PillarRepository
    ) -> None:
        self.session = session
        self.user_tz = user_tz
        self.habit_repo = habit_repo
        self.completion_repo = completion_repo
        self.pillar_repo = pillar_repo
        self.streak_calc = StreakCalculator(today=datetime.now(ZoneInfo(user_tz)).date())

    def update_habit(self, validated: HabitUpdate, habit_id: int) -> Habit:
        habit = self.habit_repo.get_by_id(habit_id)
        if not habit:
            raise ServiceError("Habit not found", 404)

        for field in validated.model_fields_set:
            if field == "pillar_ids":
                continue
            setattr(habit, field, getattr(validated, field))

        if "pillar_ids" in validated.model_fields_set:
            self._sync_pillars(habit, validated.pillar_ids)

        return habit

    def create_habit(self, validated: HabitCreate) -> Habit:
        # do the is_promotable thing
        status = self._resolve_status(validated.is_promotable)

        habit = self.habit_repo.create_habit(
            name=validated.name,
            status=status,
            target_frequency=validated.target_frequency,
        )
        self._sync_pillars(habit, validated.pillar_ids)
        self.session.flush()
        return habit

    def delete_habit(self, habit_id: int) -> Habit:
        habit = self.habit_repo.get_by_id(habit_id)
        if habit is None:
            raise ServiceError("Habit not found", 404)
        self.habit_repo.delete(habit)
        return habit

    def get_habit(self, habit_id: int) -> Habit:
        habit = self.habit_repo.get_by_id(habit_id)
        if habit is None:
            raise ServiceError("Habit not found", 404)
        return habit

    def _resolve_status(self, is_promotable: bool) -> StatusEnum | None:
        return StatusEnum.EXPERIMENTAL if is_promotable else None

    def _sync_pillars(self, habit: Habit, pillar_ids: list[int]) -> None:
        habit.pillars = self.pillar_repo.get_by_ids(pillar_ids)


    def save_completion(self, habit_id: int, completed_on: date) -> tuple[HabitCompletion, dict[str, Any]]:
        habit = self.habit_repo.get_by_id(habit_id)
        if not habit:
            raise ServiceError("Habit not found", 404)

        completion = self.completion_repo.create_habit_completion(habit.id, completed_on)
        self.session.flush()

        self.check_promotion(habit)
        progress = self.calculate_all_habits_percentage_this_week()
        return completion, progress

    def delete_completion(self, habit_id: int, date_str: str) -> dict[str, Any]:
        if date_str == "today":
            day = datetime.now(ZoneInfo(self.user_tz)).date()
        else:
            day = date.fromisoformat(date_str)
            # start_utc, end_utc = dth.day_range_utc(parsed_date, self.user_tz)

        completion = self.completion_repo.get_in_window(day, day + timedelta(days=1), habit_id=habit_id)
        if not completion:
            raise ServiceError("No completion found", 404)

        self.completion_repo.delete(completion[0])
        # self.check_promotion(habit) # would we un-promote a habit?
        return self.calculate_all_habits_percentage_this_week()


    # Streak calc: scan completion dates looking for consecutive days
    #  Similar pattern to LC#121 (Best Time to Buy/Sell Stock) - one-pass scan with invariant
    # prices[i] <-> completion_dates[i]
    # min_price <-> anchor date (most recent valid completion)
    # max_profit <-> streak length
    def calculate_habit_streak(self, habit_id: int) -> int:
        """Calculate current streak for given habit."""
        completions = self.completion_repo.get_all_habit_completions(
            habit_id, order_desc=True
        )
        dates = [c.completed_on for c in completions]
        return self.streak_calc.current_streak(dates)

        # if not habit_completions:
        #     return 0

        # # Convert to user timezone for calendar day logic
        # user_timezone = ZoneInfo(self.user_tz)
        # today_date = datetime.now(user_timezone).date()
        # local_completion_dates = [
        #     c.created_at.astimezone(user_timezone).date() for c in habit_completions
        # ]

        # if (today_date - local_completion_dates[0]).days >= STREAK_GRACE_DAYS:
        #     return 0
        # streak = 1
        # for curr_date, prev_date in pairwise(local_completion_dates):
        #     if (curr_date - prev_date).days == 1:
        #         streak += 1
        #     else:
        #         break

        # return streak

    # TODO: De-dupe? idk
    def get_all_streaks(self) -> dict[int, int]:
        completions = self.completion_repo.get_all()

        # user_timezone = ZoneInfo(self.user_tz)
        # today_date = datetime.now(user_timezone).date()

        # Group by habit_id
        by_habit = defaultdict(list)
        for c in completions:
            by_habit[c.habit_id].append(c.completed_on)

        return {
            habit_id: self.streak_calc.current_streak(sorted(dates, reverse=True))
            for habit_id, dates in by_habit.items()
        }
        # streaks = {}
        # for habit_id, dates in by_habit.items():
        #     dates.sort(reverse=True)
        #     if (today_date - dates[0]).days >= STREAK_GRACE_DAYS:
        #         streaks[habit_id] = 0
        #         continue
        #     streak = 1
        #     for curr, prev in pairwise(dates):
        #         if (curr - prev).days == 1:
        #             streak += 1
        #         else:
        #             break
        #     streaks[habit_id] = streak

        # return streaks

    def get_streak_summary(self) -> dict[str, dict[str, Any] | None]:
        """Highest and lowest current streaks across user's habits.

        Each value is {"name": str, "days": int}, or None when no habit has any
        completions yet (nothing to compare).
        """
        streaks = self.get_all_streaks()
        if not streaks:
            return {"highest": None, "lowest": None}

        names = {h.id: h.name for h in self.habit_repo.get_all_habits_and_tags()}
        best_id, best_days = max(streaks.items(), key=lambda kv: kv[1])
        worst_id, worst_days = min(streaks.items(), key=lambda kv: kv[1])

        return {
            "highest": {"name": names[best_id], "days": best_days},
            "lowest": {"name": names[worst_id], "days": worst_days},
        }

    def check_promotion(self, habit: Habit) -> Any:
        ## Over the last N weeks, what % of the target did user actually hit?
        # range for completions, fetch records for this habit_id
        # DEBUG: Testing emit/on system actually fires:
        start_utc, end_utc = dth.last_n_days_range(days_ago=63, tz_str=self.user_tz)
        completions = self.completion_repo.get_completion_counts_by_week_in_window(habit.id, start_utc, end_utc)

        # target = this habit's target_freq * 63
        # habit = self.habit_repo.get_by_id(habit_id)
        target = habit.target_frequency

        # For each week, we wanna ask:
        # is num_completions >= this_habit.target_frequency?
        # if yes -> success, else -> subpar week
        successful_weeks = 0
        for week, count in completions:
            if count >= target:
                successful_weeks += 1

        # We now have both num_weeks and successful_weeks
        # rate = successful_weeks / 9
        rate = successful_weeks / 9
        if rate >= PROMOTION_THRESHOLD: # if we hit wkly target in at least 70% of the last 9 weeks, promote
            habit.status = StatusEnum.ESTABLISHED


    def check_if_completed_today(self, habit_id: int) -> bool:
        """
        Return True if the user completed the given habit today (according to local timezone).
        """
        day = dth.user_today(self.user_tz)
        completions = self.completion_repo.get_in_window(
            day, day + timedelta(days=1), habit_id=habit_id
        )
        return bool(completions)

    # NOTE: "Percent completion habits this week" - Mon to Sun
    # TODO: Fix this up
    def calculate_all_habits_percentage_this_week(self) -> dict[str, Any]:
        """
        Calculate aggregate habit completion progress for the current week.

        Computes total number of recorded habit completions from Mon. through today (inclusive), the
        total expected completions based on each habit's target frequency, and the resulting completion percentage.
        """
        # Determine current day in the week
        today = dth.user_today(self.user_tz)
        start_of_week = today - timedelta(days=today.weekday())

        # Fetch completions in that time range
        total_completions = len(
            self.completion_repo.get_in_window(start_of_week, today + timedelta(days=1))
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
        # TODO: fetches all completion records for user
        completion_records = self.completion_repo.get_all()

        # convert completed_on's to local date -> list of completion counts per date
        completion_records_local = [entry.completed_on for entry in completion_records]

        # group by local date + count completions per day, make dataframe from list:
        df = pd.DataFrame({ "date": completion_records_local })

        # count occurrences of each val in a col:
        # groupby("date") groups rows by unique date values
        # size() counts how many rows are in each group
        # .reset_index(name="completion_count") turns it back into a clean two-col DataFrame:
        # date and completion_count
        return df.groupby("date").size().reset_index(name="completion_count")


def create_habits_service(
    session: Session, user_id: int, user_tz: str
) -> HabitsService:
    """Factory function to instantiate HabitsService with required repositories."""
    return HabitsService(
        session=session,
        user_tz=user_tz,
        habit_repo=HabitRepository(session, user_id),
        completion_repo=HabitCompletionRepository(session, user_id),
        pillar_repo=PillarRepository(session, user_id)
    )

class StreakCalculator:
    GRACE_DAYS = 2

    def __init__(self, today: date):
        self.today = today

    def current_streak(self, dates: list[date]) -> int:
        """Dates must be in descending order"""
        if not dates:
            return 0

        # Check if streak exists (must be within 2 days of today)
        if (self.today - dates[0]).days >= self.GRACE_DAYS:
            return 0

        # Count consecutive days using pairwise()
        # pairwise() = lazy iterator, no list allocation: O(n) time, O(1) extra space
        # Stil O(n) like zip(seq, seq[1:]) would be
        streak = 1
        for curr, prev in pairwise(dates):
            if (curr - prev).days == 1:
                streak += 1
            else:
                break
        return streak
