
from sqlalchemy import Column, DateTime, Integer, String, CheckConstraint

from app._infra.db_base import Base
from app.modules.time_tracking.constants import CATEGORY_MAX_LENGTH, DESCRIPTION_MAX_LENGTH


class TimeEntry(Base):
    """Individual time entries for our time_tracking module (activity log)."""

    __table_args__ = (
        CheckConstraint("ended_at > started_at", name="ck_ended_after_started"),
    )
    
    category = Column(
        String(CATEGORY_MAX_LENGTH),  # 'Programming', 'Workout', etc
        CheckConstraint(f'length(category) > 0', name='ck_time_entry_category_non_empty'),
        nullable=False
    )

    description = Column(String(DESCRIPTION_MAX_LENGTH))
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False)

    duration_minutes = Column(
        Integer,
        CheckConstraint('duration_minutes > 0', name='ck_time_entry_duration_positive'),
        nullable=False
    )
    
    def __repr__(self):
        return f"<TimeEntry id={self.id} category='{self.category}' started_at={self.started_at}>"