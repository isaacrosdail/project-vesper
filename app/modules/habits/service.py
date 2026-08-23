"""
Habit service layer, to evaluate streaks & completions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.modules.habits.schemas import HabitCompletionCreate
from app.modules.habits.streaks import StreakCalculator
from app.shared.schemas import TargetCreate
from app.shared.target import Target

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.habits.models import Habit, HabitCompletion
    from app.modules.habits.schemas import HabitCreate
    from app.modules.habits.schemas import HabitPatch as HabitUpdate

from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import app.shared.datetime_.helpers as dth
from app.modules.habits.models import HabitTypeEnum
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

        fields = validated.model_fields_set
        if habit.type == HabitTypeEnum.BINARY and ("target" in fields or "units" in fields):
            raise ServiceError("Binary habits have no target or units", 422)
        if habit.type == HabitTypeEnum.DURATION and "units" in fields:
            raise ServiceError("Duration habits have fixed units", 422)

        for field in fields:
            if field in {"pillar_ids", "target"}:
                continue
            setattr(habit, field, getattr(validated, field))

        if "target" in fields:
            t = validated.target.to_domain() if validated.target else None
            habit.target_low = t.low if t else None
            habit.target_high = t.high if t else None

        if "pillar_ids" in fields:
            self._sync_pillars(habit, validated.pillar_ids)

        return habit

    def create_habit(self, validated: HabitCreate) -> Habit:
        type = validated.type
        units: str | None = getattr(validated, "units", None)
        target: TargetCreate | None = getattr(validated, "target", None)
        t = target.to_domain() if target else Target()

        habit = self.habit_repo.create_habit(
            name=validated.name,
            weekly_frequency=validated.weekly_frequency,
            type=type,
            units=units,
            target_low=t.low,
            target_high=t.high,
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

    def _sync_pillars(self, habit: Habit, pillar_ids: list[int]) -> None:
        habit.pillars = self.pillar_repo.get_by_ids(pillar_ids)


    def save_completion(self, habit_id: int, validated: HabitCompletionCreate) -> tuple[HabitCompletion, dict[str, Any]]:
        habit = self.get_habit(habit_id)

        if validated.entry_date > dth.user_today(self.user_tz):
            raise ServiceError("Cannot log a future date", 422)
        if habit.type == HabitTypeEnum.BINARY and validated.value is not None:
            raise ServiceError("Binary habits do not take a value", 422)
        if habit.type != HabitTypeEnum.BINARY and validated.value is None:
            raise ServiceError("This habit requires a value", 422)

        day = validated.entry_date
        existing = self.completion_repo.get_in_window(day, day + timedelta(days=1), habit_id=habit_id)
        if existing:
            completion = existing[0]
            completion.value = validated.value  # snapshot columns untouched!
        else:
            completion = self.completion_repo.create_habit_completion(
                habit_id, validated.entry_date, value=validated.value,
                target_low_snapshot=habit.target_low,
                target_high_snapshot=habit.target_high,
            )
        self.session.flush()

        progress = self.calculate_all_habits_percentage_this_week()
        return completion, progress

    def delete_completion(self, habit_id: int, date_str: str) -> dict[str, Any]:
        if date_str == "today":
            day = datetime.now(ZoneInfo(self.user_tz)).date()
        else:
            day = date.fromisoformat(date_str)

        completion = self.completion_repo.get_in_window(day, day + timedelta(days=1), habit_id=habit_id)
        if not completion:
            raise ServiceError("No completion found", 404)

        self.completion_repo.delete(completion[0])
        return self.calculate_all_habits_percentage_this_week()


    def calculate_habit_streak(self, habit_id: int) -> int:
        """Calculate current streak for given habit."""
        habit = self.habit_repo.get_by_id(habit_id)
        if not habit:
            raise ServiceError("no such habit?")
        completions = self.completion_repo.get_all_habit_completions(
            habit_id, order_desc=True
        )
        dates = [c.entry_date for c in completions if c.satisfied]
        return self.streak_calc.streak(dates, habit.weekly_frequency)


    def get_all_streaks(self) -> dict[int, int]:
        completions = self.completion_repo.get_all()
        habits = self.habit_repo.get_all()

        # Group by habit_id
        by_habit: dict[int, list[date]] = defaultdict(list)
        for c in completions:
            if c.satisfied:
                by_habit[c.habit_id].append(c.entry_date)

        return {
            h.id: self.streak_calc.streak(by_habit.get(h.id, []), h.weekly_frequency)
            for h in habits
        }

    def get_streak_summary(self) -> dict[str, dict[str, Any] | None]:
        """Highest and lowest current streaks across user's habits.

        Each value is {"name": str, "days": int}, or None when no habit has any
        completions yet (nothing to compare).
        """
        streaks = self.get_all_streaks()
        if not streaks:
            return {"highest": None, "lowest": None}

        names = {h.id: h.name for h in self.habit_repo.get_all()}
        best_id, best_days = max(streaks.items(), key=lambda kv: kv[1])
        worst_id, worst_days = min(streaks.items(), key=lambda kv: kv[1])

        return {
            "highest": {"name": names[best_id], "days": best_days},
            "lowest": {"name": names[worst_id], "days": worst_days},
        }


    def check_if_completed_today(self, habit_id: int) -> bool:
        """
        Return True if the user completed the given habit today (according to local timezone).
        """
        day = dth.user_today(self.user_tz)
        completions = self.completion_repo.get_in_window(
            day, day + timedelta(days=1), habit_id=habit_id
        )
        return any(c.satisfied for c in completions)


    def calculate_all_habits_percentage_this_week(self) -> dict[str, Any]:
        """Aggregate weekly progress: distinct satisfied days per habit,
        capped at each habit's weekly_frequency,
        against the summed weekly expected.
        """
        grouped = self.get_week_completions_by_habit()
        days_done = {
            habit_id: len({c.entry_date for c in completions if c.satisfied})
            for habit_id, completions in grouped.items()
        }

        # Expected_completions is sum of weekly_frequency for all
        habits = self.habit_repo.get_all()
        completed = sum(min(days_done.get(h.id, 0), h.weekly_frequency) for h in habits)
        expected = sum(h.weekly_frequency for h in habits)

        percent = round(completed / expected * 100) if expected > 0 else 0
        return {
            "completed": completed,
            "total": expected,
            "percent": percent,
        }

    def get_week_completions_by_habit(self) -> dict[int, list[HabitCompletion]]:
        """Current week's completions (Monday thru today) grouped by habit id."""
        today = dth.user_today(self.user_tz)
        start_of_week = today - timedelta(days=today.weekday())
        completions = self.completion_repo.get_in_window(start_of_week, today + timedelta(days=1))

        grouped: dict[int, list[HabitCompletion]] = {}
        for c in completions:
            grouped.setdefault(c.habit_id, []).append(c)
        return grouped


    def completions_summary(self, last_n_days: int) -> list[dict[str, Any]]:
        """Per-habit completion counts vs expected over the last N days.

        Zero-count habits included (left outer join by design: a neglected
        habit should show as 0/expected). Sorted by count descending.
        """
        today = dth.user_today(self.user_tz)
        window_start = today - timedelta(days=last_n_days - 1)
        counts = self.completion_repo.get_completion_counts_by_habit_in_window(
            window_start, today + timedelta(days=1)
        )

        rows: list[dict[str, Any]] = []
        for h in self.habit_repo.get_all():
            match h.schedule:
                case FrequencySchedule(weekly_frequency=freq):
                    expected = freq * last_n_days / 7
                case DatedSchedule() as s:
                    expected = len(s.intended_in_window(h.start_date, window_start, today))
            rows.append({"name": h.name, "count": counts.get(h.id, 0), "expected": expected})

        rows.sort(key=lambda r: r["count"], reverse=True)
        return rows



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
