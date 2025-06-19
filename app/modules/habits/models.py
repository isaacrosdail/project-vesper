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

    habit_completions = relationship("HabitCompletion", back_populates="habit")

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
    

# Daily Intention Model - to let intentions persist
class DailyIntention(Base):

    intention = Column(String(200))

# Daily Metric Model - Quantitative stuff: to store basic metrics like our daily steps counter, for example
class DailyMetric(Base):
    # Flexible, quantitative & objective
    metric_type = Column(String(50), nullable=False) # 'weight', 'steps', 'movement'
    unit = Column(String(20), nullable=False)         # 'lbs',    'steps', 'minutes'
    value = Column(Float)

class DailyCheckin(Base):
    # Fixed fields, quantitative & subjective
    stress_level = Column(Integer) # 1-10
    energy_level = Column(Integer) # 1-10
    mood = Column(Integer)   # maybe?
    # Can add more scales later
    
# Daily Reflection Model - Just the qualitative stuff, acts as centralized "day log"
class DailyReflection(Base):

    reflection = Column(String(2000))       # main reflection text
    accomplished = Column(String(1000))     # what I accomplished
    learned_today = Column(String(2000))
    highlights = Column(String(500))        # Optional, blend of "what went well? what was hard?"