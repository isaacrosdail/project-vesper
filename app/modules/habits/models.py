# Handles DB models for tasks module

from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db_base import Base, CustomBaseTaskMixin

# Habit/HabitCompletion
# Relationship type: one-to-many (one habit, many completions)
# Direction: bidirectional (thanks to back_populates)
# Habit Model
class Habit(Base):

    # cascade here ensures that when we delete Habits, any associated HabitCompletions are also deleted, preventing hanging/orphaned entries
    habit_completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")

    title = Column(String(255), unique=True, nullable=False)
    category = Column(String(255), nullable=False, default='misc') # Misc. category as a catch-all
    status = Column(String(50), default='experimental')     # Becomes 'established' once promoted
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
        # No completions found for today
        return False 
    
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "ID",
        "title": "Title",
        "category": "Category",
        "status": "Status",
        "created_at": "Date Added",
        "established_date": "Date Promoted",
        "promotion_threshold": "Promotion Threshold"
    }

# Habit Completion Model - enables us to track WHEN and HOW OFTEN specific habits were completed!
# Stores each "completion" as a new entry
class HabitCompletion(Base, CustomBaseTaskMixin):

    habit = relationship("Habit", back_populates="habit_completions")

    habit_id = Column(Integer, ForeignKey('habit.id'))

