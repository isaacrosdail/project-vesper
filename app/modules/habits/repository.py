# DB logic functions to access data

from .models import Habit, HabitCompletion

# Get all habits
def get_all_habits(session):
    return session.query(Habit).all()
