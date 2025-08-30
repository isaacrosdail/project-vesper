
from sqlalchemy import Column, DateTime, Float, String

from app._infra.db_base import Base


# Model for individual time entries for our activity log
class TimeEntry(Base):

    category = Column(String(50), nullable=False) # 'Programming', 'Workout', etc
    description = Column(String(200))
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Float, nullable=False) # minutes - convert at edges where desired

    def __repr__(self):
        return f"<TimeEntry id={self.id} category='{self.category}' started_at={self.started_at}"