# Handles DB models for tasks module

from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db_base import Base


# Habit/HabitCompletion
# Relationship type: one-to-many (one habit, many completions)
# Direction: bidirectional (thanks to back_populates)
# Habit Model
class Habit(Base):
    __tablename__ = "habits"

    habit_completions = relationship("HabitCompletion", back_populates="habit")

    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default='experimental')     # Becomes 'established' once promoted
    experimental_start_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    established_date = Column(DateTime(timezone=True), nullable=True)
    promotion_threshold = Column(Float, default=0.7) # 70% completion rate -> How would I code the promotion logic for this??

    # Method to filter all of a habit's completions to find the one's from today
    def completed_today(self):
        # Define "today" - UTC midnight to midnight
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Loop through ALL completions for this habit (Study later!)
        for completion in self.habit_completions: # Uses our bidirectional relationship
            # Check if completion has happened today
            if today_start <= completion.completed_at < today_end:
                return True # Found completion from today
        
        return False # No completions found for today
    
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "ID",
        "title": "Title",
        "status": "Status",
        "experimental_start_date": "Date Added",
        "established_date": "Date Promoted",
        "promotion_threshold": "Promotion Threshold"
    }

# Habit Completion Model - enables us to track WHEN and HOW OFTEN specific habits were completed!
# Stores each "completion" as a new entry
class HabitCompletion(Base):
    __tablename__ ="habit_completions"

    habit = relationship("Habit", back_populates="habit_completions")

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'))
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)) # When was it completed?

# Daily Intention Model - to let intentions truly persist as well as to serve future daily reflection stuff
class DailyIntention(Base):
    __tablename__ = "daily_intention"

    id = Column(Integer, primary_key=True)
    intention = Column(String(200))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # Consider adding stuff like success_rating and evening_reflection text?

# Daily Metric Model - to store basic metrics like our daily steps counter, for example
class DailyMetric(Base):
    __tablename__ = "daily_metric"

    id = Column(Integer, primary_key=True)
    metric_type = Column(String(50)) # ex: 'steps', 'sleep_hours', etc etc
    value = Column(Float)