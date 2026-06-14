from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.modules.auth.models import User
    from app.modules.tasks.models import Task
    from app.modules.tasks.schemas import Task as TaskCreate
    from app.modules.tasks.schemas import TaskPatch


from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

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
        due_datetime = dth.to_eod_datetime(validated.due_date, self.user_tz)

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
        return task

    def update_task(self, task_id: int, validated: TaskPatch) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ServiceError("Task not found", 404)

        # Cross-field validation
        new_priority = validated.priority if "priority" in validated.model_fields_set else task.priority
        new_due_date = validated.due_date if "due_date" in validated.model_fields_set else task.due_date
        if new_due_date is not None and "due_date" in validated.model_fields_set:
            new_due_date = dth.to_eod_datetime(new_due_date, self.user_tz)

        self._validate_frog_rule_for_values(
            priority=new_priority,
            due_date=new_due_date,
            current_task_id=task.id,
        )

        for field in validated.model_fields_set:
            if field in {"pillar_ids", "subtask_ids"}:
                continue
            value = getattr(validated, field)
            if field == "due_date" and value is not None:
                value = dth.to_eod_datetime(value, self.user_tz)
            setattr(task, field, value)

        if "pillar_ids" in validated.model_fields_set:
            self._sync_pillars(task, validated.pillar_ids)
        if "subtask_ids" in validated.model_fields_set:
            self._sync_subtasks(task, validated.subtask_ids)

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
        due_date: datetime,
        current_task_id: int | None,
    ) -> None:
        if priority is not PriorityEnum.FROG or due_date is None:
            return

        start_utc, end_utc = dth.day_range_utc(due_date.date(), self.user_tz)
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

    def _sync_pillars(self, task: Task, pillar_ids: list[int]) -> None:
        # return self.pillar_repo.get_by_ids(pillar_ids)
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

    # def to_eod_datetime(self, date: date | None, tz_str: str) -> datetime | None:
    #     """Convert a date to exclusive EOD datetime in given timezone."""
    #     if not date:
    #         return None
    #     tz = ZoneInfo(tz_str)
    #     start_of_day = datetime.combine(date, time.min, tzinfo=tz)
    #     eod_midnight = start_of_day + timedelta(days=1)
    #     return eod_midnight - timedelta(seconds=1)

    # TODO: we could use created_at_local :/
    def calculate_tasks_progress_today(self) -> dict[str, Any]:
        all_tasks = self.task_repo.get_all()

        # Count completed vs expected for today
        num_completed, num_expected = 0, 0

        for task in all_tasks:
            due_today = task.due_date and dth.is_same_local_date(
                task.due_date, self.user_tz
            )
            completed_today = task.completed_at and dth.is_same_local_date(
                task.completed_at, self.user_tz
            )

            # TODO: Old, scrap once match/case variant is confirmed fine
            # if due_today:
            #     num_expected += 1
            #     if completed_today:
            #         num_completed += 1

            # elif completed_today and task.due_date is None:
            #     # "spontaneous" task, completed today without a due date
            #     num_completed += 1
            #     num_expected += 1

            # Match/case here makes the truth table visible?
            match (bool(due_today), bool(completed_today), task.due_date is None):
                case (True, True, _):
                    num_expected += 1
                    num_completed += 1
                case (True, False, _):
                    num_expected += 1
                case (False, True, True):
                    num_expected += 1
                    num_completed += 1

        percent_complete = (
            (num_completed / num_expected * 100) if num_expected > 0 else 0
        )

        return {
            "completed": num_completed,
            "total": num_expected,
            "percent": percent_complete,
        }

    # TODO: make sure this is even right
    def calc_overdue_rate(self, *, days: int) -> dict[str, int]:
        """Takes int val for days 'into the past' to check against, and returns """
        ## take all tasks where due_date != None and falls within last N days
        ## of those - count where is_done = False, those are the ones overdue
        ## Rate = overdue / total as percentage
        now = dth.now_utc()
        start = now - timedelta(days=days)

        tasks_in_window = self.task_repo.get_all_in_window(start, now, date_col="due_date")
        total = len(tasks_in_window)
        if total == 0:
            return { "rate": 0, "overdue": 0, "total": 0 }
        overdue = len([t for t in tasks_in_window if not t.is_done])
        rate = round((overdue/total) * 100)

        return { "rate": rate, "overdue": overdue, "total": total }

    def calc_frog_completion_rate(self, *, days: int) -> dict[str, int]:
        now = dth.now_utc()
        start = now - timedelta(days=days)

        tasks = self.task_repo.get_all_in_window(start, now, date_col="due_date")
        frogs = [t for t in tasks if t.is_frog]
        total = len(frogs)
        if total == 0:
            return { "rate": 0, "done": 0, "total": 0 }

        done = len([t for t in frogs if t.is_done])
        rate = round((done / total) * 100)

        return { "rate": rate, "done": done, "total": total }


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
