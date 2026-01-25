from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.modules.time_tracking.validation_constants import (
    CATEGORY_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
)
from app.shared.datetime_.helpers import convert_to_timezone
from app.shared.serialization import APISerializable


class TimeEntry(Base, APISerializable):
    """Individual time entries for our time_tracking module (activity log)."""

    __table_args__ = (
        CheckConstraint("ended_at > started_at", name="ck_ended_after_started"),
        CheckConstraint("duration_minutes > 0", name="ck_time_entry_duration_positive"),
        CheckConstraint(
            "length(category) > 0", name="ck_time_entry_category_non_empty"
        ),
    )

    category: Mapped[str] = mapped_column(
        String(CATEGORY_MAX_LENGTH),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(String(DESCRIPTION_MAX_LENGTH))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    user = relationship("User", back_populates="time_entry")

    @property
    def started_at_local(self) -> datetime:
        return convert_to_timezone(self.user.timezone, self.started_at)

    @property
    def ended_at_local(self) -> datetime:
        return convert_to_timezone(self.user.timezone, self.ended_at)

    def __repr__(self) -> str:
        return f"<TimeEntry id={self.id} category='{self.category}' started_at={self.started_at}>"
