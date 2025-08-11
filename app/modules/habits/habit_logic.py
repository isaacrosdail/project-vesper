# Business logic functions for habits module

from datetime import datetime, timezone
from app.common.sorting import bubble_sort
from app.modules.habits.models import Habit, HabitCompletion
from app.core.database import database_connection
from sqlalchemy import func

# Originally prototyped in playground3.py - see that for notes
def calculate_habit_streak(habit_id, user_id, session):

    # Fetch all HabitCompletions for given habit
    habit_completions = session.query(HabitCompletion).join(Habit).filter(
        HabitCompletion.habit_id == habit_id,
        Habit.user_id == user_id, # Ensure habit belongs to this user
    ).all()

    # Streak is naturally 0 if there simply are no completions :P
    if not habit_completions:
        return 0

    # Step 1: Sort the completions with most recent datetime first
    bubble_sort(habit_completions, 'created_at', reverse=True)

    # Step 2: First check whether a streak exists at all
    # if today is within 2 days of completion[0] -> then YES
    # if not -> don't bother, we have no streak!
    if (datetime.now(timezone.utc) - habit_completions[0].created_at).days < 2:
        # Have a streak, now loop through completions and sum consecutive days
        total_streak = 1
        for i in range(len(habit_completions) - 1): # Remember: -1 here to avoid out of bounds!
            if (habit_completions[i].created_at - habit_completions[i+1].created_at).days == 1:
                total_streak += 1
            else:
                break # gap found, streak ends here!
        return total_streak
    else:
        return 0

def check_if_completed_today(habit_id, user_id, session):
    # Get today in UTC, strip datetime using date() for comparison below
    today_utc = datetime.now(timezone.utc).date()
    
    def _do_check(s):
        # query habitcompletion table, need matching habit_id and completed_at = today
        habit_completion = s.query(HabitCompletion).join(Habit).filter(
                HabitCompletion.habit_id == habit_id,
                Habit.user_id == user_id,
                func.date(HabitCompletion.created_at) == today_utc
        ).first()

        return habit_completion is not None  # return true if exists, false if not
    
    if session:
        return _do_check(session)
    else:
        with database_connection() as session:
            return _do_check(session)