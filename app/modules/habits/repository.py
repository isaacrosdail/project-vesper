# DB logic functions to access data

from .models import Habit, HabitCompletion, DailyIntention
from sqlalchemy import func
from datetime import date
# Get all habits
def get_all_habits(session):
    return session.query(Habit).all()

# Get today's daily intention
def get_today_intention(session):
    today = date.today()

    todayIntention = session.query(DailyIntention).filter(
        func.date(DailyIntention.created_at) == today
    ).first()
    
    return todayIntention