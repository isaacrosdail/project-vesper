# For created_at / completed_at
from datetime import datetime

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from app.common.sorting import bubble_sort

from app.core.database import database_connection
# Import Habit repository
from app.modules.habits import repository as habits_repo
# Import Habit, HabitCompletion model
from app.modules.habits.models import Habit, HabitCompletion

from flask_login import login_required, current_user

habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")


@habits_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    with database_connection() as session:
        # Fetch Habits & pass into template
        # Column names for Habit model
        habit_column_names = [
            Habit.COLUMN_LABELS.get(col, col)
            for col in Habit.__table__.columns.keys()
        ]

        # Fetch list of Habits, sort by most recent
        habits = habits_repo.get_user_habits(session, current_user.id)
        bubble_sort(habits, 'created_at', reverse=True)

        return render_template(
            "habits/dashboard.html",
            habit_column_names = habit_column_names,
            habits = habits
        )

# CREATE
@habits_bp.route("/", methods=["GET", "POST"])
@login_required
#TODO: Rename?
def habits():

    # Process form data and add new habit to db
    if request.method == "POST":

        # Create new habit object
        new_habit = Habit(
            title = request.form.get("title"),
            category=request.form.get("category"),
            user_id=current_user.id
        )

        with database_connection() as session:
        # Add new_habit to db
            session.add(new_habit)
            flash(f"Habit added successfully.") # flash confirmation

            return redirect(url_for("habits.dashboard")) # Redirect after POST - NOT render_template
            # Follows Post/Redirect/Get (PRG) pattern

    # GET => Return add_habit form page
    else:
        return render_template("habits/add_habit.html")
    
# Creates a new HabitCompletion record to mark a Habit complete & enable more robust habit analytics in future
@habits_bp.route("/<int:habit_id>/completions", methods=["POST"])
@login_required
# TODO: Rename?
def completions(habit_id):
    
    try:
        with database_connection() as session:
            # Verify habit belongs to current user first
            habit = session.query(Habit).filter(
                Habit.id == habit_id,
                Habit.user_id == current_user.id
            ).first()

            if not habit:
                return jsonify({"success": False, "message": "Habit not found"}), 404
            
            # So we have the habit_id and need to make a new HabitCompletion entry using that as its foreignkey
            # Just have primary key and date default otherwise, so don't need to specify/add those
            new_habit_completion = HabitCompletion(
                habit_id = habit_id,
                user_id=current_user.id
            )
            session.add(new_habit_completion)
            return jsonify({"success": True, "message": "Habit marked complete"}), 201 # 201 = Created (success for POST)
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to mark habit complete"}), 500
    

# Deletes a given HabitCompletion record (acts as our "habit marked complete")
# For now, we'll only allow habits to have a single completion record in a given day
# BUT this is now flexible enough to allow for choosing the day whose completion we wish to delete
@habits_bp.route("/<int:habit_id>/completions", methods=["DELETE"])
@login_required
# TODO: Rename?
def completion(habit_id):
    from datetime import date
    # Instead of /today in route, pass desired day in as arg/param
    # Want to be able to receive date string from HTTP like "2025-06-26"
    date_received = request.args.get('date', 'today') # default to today

    if date_received == 'today':
        # handle default case
        date_only = date.today()
    else:
        # Handle actual date string case => Turn date string into datetime obj first
        date_obj = datetime.strptime(date_received, "%Y-%m-%d") # Format "2025-06-26 00:00:00"
        date_only = date_obj.date() # Then get date ONLY (no time)

    try:
        with database_connection() as session:
            # Find corresponding habitcompletion entry for today
            habit_completion = habits_repo.get_user_today_habit_completions(session, current_user.id, habit_id, date_only)

            # habit_completion = session.query(HabitCompletion).join(Habit).filter(
            #     HabitCompletion.habit_id == habit_id,
            #     Habit.user_id == current_user.id,
            #     func.date(HabitCompletion.created_at) == date_only
            # ).first()
    
            if habit_completion:
                session.delete(habit_completion)
                return jsonify({"success": True, "message": "Habit unmarked as complete"}), 200
            else:
                return jsonify({"success": False, "message": "No completion found for today"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to unmark habit"}), 500 # 500 = Internal Server Error