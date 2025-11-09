
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app._infra.db_base import Base
from app.shared.serialization import APISerializable
from app.modules.time_tracking.constants import CATEGORY_MAX_LENGTH, DESCRIPTION_MAX_LENGTH


class TimeEntry(Base, APISerializable):
    """Individual time entries for our time_tracking module (activity log)."""

    __table_args__ = (
        CheckConstraint("ended_at > started_at", name="ck_ended_after_started"),
        CheckConstraint('duration_minutes > 0', name='ck_time_entry_duration_positive'),
        CheckConstraint(f'length(category) > 0', name='ck_time_entry_category_non_empty'),
    )
    
    category: Mapped[str] = mapped_column(
        String(CATEGORY_MAX_LENGTH),  # 'Programming', 'Workout', etc
        nullable=False
    )

    description: Mapped[str] = mapped_column(String(DESCRIPTION_MAX_LENGTH))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    def __repr__(self) -> str:
        return f"<TimeEntry id={self.id} category='{self.category}' started_at={self.started_at}>"
