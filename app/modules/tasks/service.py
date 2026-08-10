from __future__ import annotations

from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.orm import Session

    from app.modules.tasks.schemas import TaskCreate
    from app.modules.tasks.schemas import TaskPatch

from app.modules.tasks.models import Task

from datetime import datetime

import app.shared.datetime_.helpers as dth
from app.modules.tasks.models import PriorityEnum
from app.modules.tasks.repository import TaskRepository
from app.shared.exceptions import ServiceError
from app.shared.fractional_indexing import generate_key_between
from app.shared.repository.pillar import PillarRepository
from app.shared.utils import is_acyclic


class TasksService:
    def __init__(
        self,
        session: Session,
        user_tz: str,
        task_repo: TaskRepository,
        pillar_repo: PillarRepository
    ) -> None:
        self.session = session
        self.task_repo = task_repo
        self.user_tz = user_tz
        self.pillar_repo = pillar_repo

    def create_task(self, validated: TaskCreate) -> Task:
        due_datetime = None
        if validated.due_date is not None:
            converted = validated.due_date.astimezone(ZoneInfo(self.user_tz)).date()
            due_datetime = dth.to_eod_datetime(converted, self.user_tz)

        self._validate_frog_rule(validated)

        # Generate fractional indexing key as last in list:
        new_key = generate_key_between(self.task_repo.get_max_sort_key(), None)

        task = self.task_repo.create_task(
            name=validated.name,
            priority=validated.priority,
            due_date=due_datetime,
            sort_key=new_key
        )
        self._sync_pillars(task, validated.pillar_ids)
        self._sync_subtasks(task, validated.subtask_ids)
        self._sync_supertasks(task, validated.supertask_ids)
        self.task_repo.session.flush()
        return task

    def update_task(self, task_id: int, validated: TaskPatch) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ServiceError("Task not found", 404)

        # Cross-field validation
        new_priority = validated.priority if "priority" in validated.model_fields_set else task.priority
        new_due_date = validated.due_date if "due_date" in validated.model_fields_set else task.due_date
        if new_due_date is not None and "due_date" in validated.model_fields_set:
            converted = new_due_date.astimezone(ZoneInfo(self.user_tz)).date()
            new_due_date = dth.to_eod_datetime(converted, self.user_tz)

        self._validate_frog_rule_for_values(
            priority=new_priority,
            due_date=new_due_date,
            current_task_id=task.id,
        )

        for field in validated.model_fields_set:
            if field in {"pillar_ids", "subtask_ids", "supertask_ids"}:
                continue
            value = getattr(validated, field)
            if field == "due_date" and value is not None:
                converted = value.astimezone(ZoneInfo(self.user_tz)).date()
                value = dth.to_eod_datetime(converted, self.user_tz)
            setattr(task, field, value)

        if "pillar_ids" in validated.model_fields_set:
            self._sync_pillars(task, validated.pillar_ids)
        if "subtask_ids" in validated.model_fields_set:
            self._sync_subtasks(task, validated.subtask_ids)
        if "supertask_ids" in validated.model_fields_set:
            self._sync_supertasks(task, validated.supertask_ids)

        return task

    def delete_task(self, task_id: int) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if task is None:
            raise ServiceError("Task not found", 404)
        self.task_repo.delete(task)
        return task

    def get_task(self, task_id: int) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if task is None:
            raise ServiceError("Task not found", 404)
        return task

    def _validate_frog_rule(self, validated: TaskCreate | TaskPatch) -> None:
            self._validate_frog_rule_for_values(
                priority=validated.priority,
                due_date=validated.due_date,
                current_task_id=None,
            )

    def _validate_frog_rule_for_values(
        self,
        *,
        priority: PriorityEnum | None,
        due_date: datetime | None,
        current_task_id: int | None,
    ) -> None:
        if priority is not PriorityEnum.FROG:
            return
        if due_date is None:
            raise ServiceError("Frog tasks must have a due date")

        converted = due_date.astimezone(ZoneInfo(self.user_tz)).date()
        start_utc, end_utc = dth.day_range_utc(converted, self.user_tz)
        existing_frog = self.task_repo.get_frog_task_in_window(start_utc, end_utc)

        if existing_frog and existing_frog.id != current_task_id:
            frog_date = due_date.date().isoformat()
            raise ServiceError(f"Pre-existing 'frog' task for {frog_date}")


    def _sync_subtasks(self, task: Task, subtask_ids: list[int]) -> None:
        incoming_ids = set(subtask_ids)
        current_ids = {s.id for s in task.subtasks}

        for subtask_id in incoming_ids - current_ids:
            self.save_link(subtask_id, task.id)
        for subtask_id in current_ids - incoming_ids:
            self.delete_link(subtask_id, task.id)

    def _sync_supertasks(self, task: Task, supertask_ids: list[int]) -> None:
        incoming = set(supertask_ids)
        current = {s.id for s in task.supertasks}

        for supertask_id in incoming - current:
            self.save_link(task.id, supertask_id)
        for supertask_id in current - incoming:
            self.delete_link(task.id, supertask_id)


    def _sync_pillars(self, task: Task, pillar_ids: list[int]) -> None:
        task.pillars = self.pillar_repo.get_by_ids(pillar_ids)


    def save_link(self, subtask_id: int, supertask_id: int) -> None:
        subtask = self.task_repo.get_by_id(subtask_id)
        supertask = self.task_repo.get_by_id(supertask_id)
        if not subtask or not supertask:
            raise ServiceError("Task not found", 404)
        if subtask in supertask.subtasks or supertask in subtask.subtasks:
            raise ServiceError("Link already exists")

        links = self.task_repo.get_all_links()
        links.append((subtask_id, supertask_id))
        if not is_acyclic(links):
            raise ServiceError("Cycle in links! Rejecting link add", 400)
        supertask.subtasks.append(subtask)


    def delete_link(self, subtask_id: int, supertask_id: int) -> None:
        subtask = self.task_repo.get_by_id(subtask_id)
        supertask = self.task_repo.get_by_id(supertask_id)
        if not subtask or not supertask:
            raise ServiceError("Task not found", 404)
        if subtask not in supertask.subtasks:
            raise ServiceError("Link not found", 404)
        supertask.subtasks.remove(subtask)


    def _rate(self, tasks: list[Task], predicate: Callable[[Task], bool], *, subset_key: str) -> dict[str, Any]:
        total = len(tasks)
        subset = sum(1 for t in tasks if predicate(t))
        rate = round((subset / total) * 100) if total > 0 else 0
        return { "rate": rate, subset_key: subset, "total": total }

    # TODO: we could use created_at_local :/
    def calculate_tasks_progress_today(self) -> dict[str, int]:
        """Completion progress over today's pile of tasks.

        The pile (denominator) is every task that:
        - tasks due today, done or not.
        - overdue and still open tasks.
        - completed today, whatever due date it was (or wasn't)
        
        Completed (numerator) is the pile tasks that are done.

        Returns {"completed", "total", "percent"}.
        """
        all_tasks = self.task_repo.get_all()
        now = dth.now_utc()

        def in_pile(t: Task) -> bool:
            due_today = t.due_date and dth.is_same_local_date(t.due_date, self.user_tz)
            completed_today = t.completed_at and dth.is_same_local_date(t.completed_at, self.user_tz)
            return bool(due_today or t.is_overdue(now) or completed_today)

        pile = [t for t in all_tasks if in_pile(t)]
        total = len(pile)
        completed = sum(1 for t in pile if t.is_done)

        pct_complete = (
            (completed / total * 100) if total > 0 else 0
        )
        return { "completed": completed, "total": total, "percent": int(pct_complete) }


    def calc_overdue_rate(self, *, days: int) -> dict[str, int]:
        """Overdue rate over the last N days.
        
        Of tasks whose due date falls in the window and has already
        passed (due_date < now), the fraction still not done. Tasks due
        later today are not yet overdue and are excluded.
        """
        now = dth.now_utc()
        start_utc, _ = dth.last_n_days_range(days, self.user_tz)
        tasks = self.task_repo.get_all_in_window(start_utc, now, date_col=Task.due_date)
        return self._rate(tasks, lambda t: t.is_overdue(now), subset_key="overdue")


    def calc_frog_adherence_rate(self, *, days: int) -> dict[str, int]:
        """Frog adherence rate over the last N days.
        
        Of frogs whose due day has finished (due_date < now), the fraction
        completed on or before their due date. Today's frog is excluded
        until its day ends, and late completions do not count.
        """
        now = dth.now_utc()
        start_utc, _ = dth.last_n_days_range(days, self.user_tz)
        frogs = [
            t for t in self.task_repo.get_all_in_window(start_utc, now, date_col=Task.due_date)
            if t.is_frog
        ]
        return self._rate(
            frogs,
            lambda t: t.completed_at is not None and t.completed_at <= t.due_date,
            subset_key="done"
        )


def create_tasks_service(session: Session, user_id: int, user_tz: str) -> TasksService:
    """Factory function to instantiate HabitsService with required repositories."""
    return TasksService(
        session=session,
        user_tz=user_tz,
        task_repo=TaskRepository(session, user_id),
        pillar_repo=PillarRepository(session, user_id)
    )


# @register_patch_hook("tasks")
# def tasks_patch_hook(
#     item: Any, data: Any, session: Session, current_user: User
# ) -> dict[str, Any]:
#     """Invoked by generalized PATCH route to re-calculate tasks progress upon changes."""
#     tasks_service = create_tasks_service(
#         session, current_user.id, current_user.timezone
#     )
#     progress = tasks_service.calculate_tasks_progress_today()
#     return {"progress": progress}
