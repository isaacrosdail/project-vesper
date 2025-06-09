# DB logic functions to access data

from .models import Habit, HabitCompletion, DailyIntention
from sqlalchemy import func
from datetime import datetime, timezone
# Get all habits
def get_all_habits(session):
    return session.query(Habit).all()

# Get today's daily intention
def get_today_intention(session):

    # Get today in UTC
    today_utc = datetime.now(timezone.utc).date()

    todayIntention = session.query(DailyIntention).filter(
        func.date(DailyIntention.created_at) == today_utc
    ).first()
    
    return todayIntention