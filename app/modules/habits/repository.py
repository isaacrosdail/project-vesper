# DB logic functions to access data

from .models import Habit, HabitCompletion
from sqlalchemy import func


# Get all habits for given user id
def get_user_habits(session, user_id):
    return session.query(Habit).filter(Habit.user_id==user_id).all()

# Get today's habit completions for a given user id
def get_user_today_habit_completions(session, user_id, habit_id, date):
    return session.query(HabitCompletion).join(Habit).filter(
        HabitCompletion.habit_id == habit_id,
        Habit.user_id == user_id,
        func.date(HabitCompletion.created_at) == date
    ).first()