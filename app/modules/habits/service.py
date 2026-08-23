"""
Habit service layer, to evaluate streaks & completions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.modules.habits.schemas import PARAM_BY_MODE, HabitCompletionCreate
from app.modules.habits.streaks import StreakCalculator
from app.shared.schemas import TargetCreate
from app.shared.target import Target

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.habits.models import Habit, HabitCompletion
    from app.modules.habits.schemas import HabitCreate
    from app.modules.habits.schemas import HabitPatch

from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import app.shared.datetime_.helpers as dth
from app.modules.habits.models import DatedSchedule, FrequencySchedule, HabitTypeEnum
from app.modules.habits.repository import (
    HabitCompletionRepository,
    HabitRepository,
)
from app.shared.exceptions import ServiceError
from app.shared.repository.pillar import PillarRepository

SCHEDULE_FIELDS = {"schedule_type", *PARAM_BY_MODE.values()}

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
        self.streak_calc = StreakCalculator(today=dth.user_today(user_tz))

    def update_habit(self, validated: HabitPatch, habit_id: int) -> Habit:
        habit = self.habit_repo.get_by_id(habit_id)
        if habit is None:
            raise ServiceError("Habit not found", 404)

        fields = validated.model_fields_set
        if habit.type == HabitTypeEnum.BINARY and ("target" in fields or "units" in fields):
            raise ServiceError("Binary habits have no target or units", 422)
        if habit.type == HabitTypeEnum.DURATION and "units" in fields:
            raise ServiceError("Duration habits have fixed units", 422)

        for field in fields:
            if field in {"pillar_ids", "target"} | SCHEDULE_FIELDS:
                continue
            setattr(habit, field, getattr(validated, field))

        if "target" in fields:
            t = validated.target.to_domain() if validated.target else None
            habit.target_low = t.low if t else None
            habit.target_high = t.high if t else None

        if validated.pillar_ids is not None:
            self._sync_pillars(habit, validated.pillar_ids)

        if validated.schedule_type is not None:
            for f in SCHEDULE_FIELDS:
                setattr(habit, f, getattr(validated, f))

        return habit

    def create_habit(self, validated: HabitCreate) -> Habit:
        type = validated.type
        units: str | None = getattr(validated, "units", None)
        target: TargetCreate | None = getattr(validated, "target", None)
        t = target.to_domain() if target else Target()
        start_date = validated.start_date or dth.user_today(self.user_tz)

        habit = self.habit_repo.create_habit(
            name=validated.name,
            type=type,
            schedule_type=validated.schedule_type,
            start_date=start_date,
            weekly_frequency=validated.weekly_frequency,
            scheduled_days=validated.scheduled_days,
            monthly_days=validated.monthly_days,
            interval_days=validated.interval_days,
            units=units,
            target_low=t.low,
            target_high=t.high,
            end_date=validated.end_date,

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
        dates = {c.entry_date for c in completions if c.satisfied}
        return self.streak_calc.streak(habit, dates)


    def get_all_streaks(self) -> dict[int, int]:
        completions = self.completion_repo.get_all()
        habits = self.habit_repo.get_all()

        # Group by habit_id
        by_habit: dict[int, set[date]] = defaultdict(set)
        for c in completions:
            if c.satisfied:
                by_habit[c.habit_id].add(c.entry_date)

        return {
            h.id: self.streak_calc.streak(h, by_habit.get(h.id, set()))
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
            habit_id: {c.entry_date for c in completions if c.satisfied}
            for habit_id, completions in grouped.items()
        }

        # Expected_completions is sum of weekly_frequency for all
        habits = self.habit_repo.get_all()
        monday = dth.week_start(dth.user_today(self.user_tz))
        sunday = monday + timedelta(days=6)

        expected = 0
        completed = 0
        for h in habits:
            match h.schedule:
                case FrequencySchedule(weekly_frequency=freq):
                    expected += freq
                    completed += min(len(days_done.get(h.id, set())), freq)
                case _:
                    intended = {d for d in h.schedule.intended_dates(h.start_date, sunday) if d >= monday}
                    expected += len(list(intended))
                    completed += len(days_done.get(h.id, set()) & set(intended))

        percent = round(completed / expected * 100) if expected > 0 else 0
        return {
            "completed": completed,
            "total": expected,
            "percent": percent,
        }

    def get_week_completions_by_habit(self) -> dict[int, list[HabitCompletion]]:
        """Current week's completions (Monday thru today) grouped by habit id."""
        today = dth.user_today(self.user_tz)
        completions = self.completion_repo.get_in_window(dth.week_start(today), today + timedelta(days=1))

        grouped: dict[int, list[HabitCompletion]] = {}
        for c in completions:
            grouped.setdefault(c.habit_id, []).append(c)
        return grouped

    def week_intended_by_habit(self) -> dict[int, list[date] | None]:
        """Current week's (Mon-Sun) intended dates per habit; None for frequency mode."""
        today = dth.user_today(self.user_tz)
        monday = dth.week_start(today)
        result: dict[int, list[date] | None] = {}
        for h in self.habit_repo.get_all():
            match h.schedule:
                case FrequencySchedule():
                    result[h.id] = None
                case DatedSchedule() as s:
                    result[h.id] = sorted(
                        s.intended_in_window(h.start_date, monday, monday + timedelta(days=6))
                    )
        return result

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

    def calc_consistency_all(self) -> dict[int, int | None]:
        today = dth.user_today(self.user_tz)
        this_monday = dth.week_start(today)
        window_start = this_monday - timedelta(days=28)
        window_mondays = [this_monday - timedelta(days=n) for n in (28,21,14,7)]

        completions = self.completion_repo.get_in_window(
            this_monday - timedelta(days=28), this_monday
        )
        satisfied_days: dict[int, set[date]] = {}
        for c in completions:
            if c.satisfied:
                satisfied_days.setdefault(c.habit_id, set()).add(c.entry_date)

        result: dict[int, int | None] = {}
        for h in self.habit_repo.get_all():
            done_days = satisfied_days.get(h.id, set())
            match h.schedule:
                case FrequencySchedule(weekly_frequency=freq):
                    weeks_since = sum(1 for m in window_mondays if m >= h.start_date)
                    num_expected = freq * weeks_since
                    done = len(done_days)
                case _:
                    intended = h.schedule.intended_in_window(h.start_date, window_start, this_monday - timedelta(days=1))
                    num_expected = len(intended)
                    done = len(done_days & intended)

            result[h.id] = (
                None if num_expected == 0
                else min(100, round(100 * done / num_expected))
            )
        return result

    def get_habit_stats(self, habit_id: int) -> tuple[Habit, int, int]:
        """Finds days_missed and best_streak for a given habit."""
        habit = self.get_habit(habit_id)
        completions = self.completion_repo.get_all_habit_completions(
            habit.id, order_desc=True
        )
        satisfied = {c.entry_date for c in completions if c.satisfied}
        _, best_streak = self.streak_calc.streaks(habit, satisfied)
        days_missed = self.streak_calc.days_missed(habit, satisfied)
        return habit, days_missed, best_streak


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
