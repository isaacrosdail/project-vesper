
from app._infra.db_base import Base
from sqlalchemy import Column, DateTime, Float, String


# Model for individual time entries for our activity log
class TimeEntry(Base):

    category = Column(String(50), nullable=False) # 'Programming', 'Workout', etc
    description = Column(String(200))
    started_at = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Float, nullable=False) # minutes as standard - convert UI-side if needed