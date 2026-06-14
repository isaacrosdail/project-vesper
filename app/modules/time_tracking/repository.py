"""
Repository layer for time_tracking module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session

from sqlalchemy import func, select

from app.modules.time_tracking.models import TimeEntry
from app.shared.models import Pillar, time_entry_pillars
from app.shared.repository.base import BaseRepository


class TimeEntryRepository(BaseRepository[TimeEntry]):
    def __init__(self, session: Session, user_id: int) -> None:
        super().__init__(session, user_id, model_cls=TimeEntry)

    def create_time_entry(
        self,
        category: str,
        started_at: datetime,
        ended_at: datetime,
        duration_minutes: float,
        description: str | None = None,
        pillar_ids: list[int] | None = None,
    ) -> TimeEntry:
        time_entry = TimeEntry(
            user_id=self.user_id,
            category=category,
            started_at=started_at,
            duration_minutes=duration_minutes,
            ended_at=ended_at,
            description=description,
        )
        # TODO: fixup
        if pillar_ids:
            stmt = select(Pillar).where(
                Pillar.id.in_(pillar_ids),
                Pillar.user_id == self.user_id
            )
            result = list(self.session.execute(stmt).scalars().all())
            time_entry.pillars = result
        return self.add(time_entry)

    def get_all_time_entries_in_window(
        self, start_utc: datetime, end_utc: datetime
    ) -> list[TimeEntry]:
        stmt = (
            self._user_select(TimeEntry)
            # .options(selectinload(TimeEntry.pillars))
            .where(
                TimeEntry.started_at >= start_utc,
                TimeEntry.ended_at < end_utc,
            )
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_overlapping_entries(self, start_utc: datetime, end_utc: datetime, exclude_id: int | None = None) -> list[TimeEntry]:
        stmt = self._user_select(TimeEntry).where(
            TimeEntry.started_at < end_utc,
            TimeEntry.ended_at > start_utc
        )
        if exclude_id is not None:
            stmt = stmt.where(TimeEntry.id != exclude_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_entries_by_category_in_window(
        self,
        category: str,
        start_utc: datetime,
        end_utc: datetime,
        *,
        order_desc: bool = True,
    ) -> list[TimeEntry]:
        """Get all entries of a given category within a certain datetime window."""
        stmt = self._user_select(TimeEntry).where(
            TimeEntry.category == category,
            TimeEntry.started_at >= start_utc,
            TimeEntry.started_at < end_utc,
        )
        if order_desc:
            stmt = stmt.order_by(TimeEntry.started_at.desc())
        return list(self.session.execute(stmt).scalars().all())

    def get_aggregates_in_window(self, start_utc: datetime) -> dict[str, float] | None:
        """Get average values for each metric field since the given datetime.
        Returns `None` if no entries exist in the window.
        """
        ## TODO: Pillars fixup
        stmt = (
            select(
                Pillar.name,
                func.sum(TimeEntry.duration_minutes).label("total_minutes")
            )
            .join(time_entry_pillars, TimeEntry.id == time_entry_pillars.c.time_entry_id)
            .join(Pillar, time_entry_pillars.c.pillar_id == Pillar.id)
            .where(
                TimeEntry.started_at >= start_utc,
                TimeEntry.user_id == self.user_id
            )
            .group_by(Pillar.name)
        )
        rows = self.session.execute(stmt).all()
        if rows is None:
            return None
        return {name: float(total) for name, total in rows}
