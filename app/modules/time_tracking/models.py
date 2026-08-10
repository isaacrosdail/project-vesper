from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app._infra.db_base import Base
from app.shared.models import Pillar, time_entry_pillars

CATEGORY_MAX_LENGTH = 50
DESCRIPTION_MAX_LENGTH = 200


class TimeEntry(Base):
    """Individual time entries for our time_tracking module (activity log)."""

    __table_args__ = (
        CheckConstraint("ended_at > started_at", name="ck_ended_after_started"),
        CheckConstraint("duration_minutes > 0", name="ck_time_entry_duration_positive"),
        CheckConstraint(
            "length(category) > 0", name="ck_time_entry_category_non_empty"
        ),
        Index("ix_time_entries_user_started_at", "user_id", "started_at"),
    )

    category: Mapped[str] = mapped_column(
        String(CATEGORY_MAX_LENGTH),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(String(DESCRIPTION_MAX_LENGTH), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    pillars: Mapped[list[Pillar]] = relationship("Pillar", secondary=time_entry_pillars, back_populates="time_entries", lazy="selectin")

    def __repr__(self) -> str:
        return f"<TimeEntry id={self.id} category='{self.category}' started_at={self.started_at}>"
