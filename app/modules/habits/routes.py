# For created_at / completed_at
from datetime import datetime, timezone

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from sqlalchemy import func

from app.core.database import db_session
# Import Habit repository
from app.modules.habits import repository as habits_repo
# Import Habit, HabitCompletion model
from app.modules.habits.models import Habit, HabitCompletion

habits_bp = Blueprint('habits', __name__, template_folder="templates", url_prefix="/habits")

@habits_bp.route("/", methods=["GET"])
def dashboard():
    # Fetch Habits & pass into template
    session = db_session()
    try:
        # Column names for Habit model
        habit_column_names = [
            Habit.COLUMN_LABELS.get(col, col)
            for col in Habit.__table__.columns.keys()
        ]

        # Fetch Habits list
        habits = habits_repo.get_all_habits(session)

        # Sort habits list by most recent DateTime first
        habits.sort(key=lambda habit: habit.experimental_start_date, reverse=True)

        return render_template(
            "habits/dashboard.html",
            habit_column_names = habit_column_names,
            habits = habits
        )
    finally:
        session.close()

# CREATE
@habits_bp.route("/add", methods=["GET", "POST"])
def add_habit():

    # Process form data and add new habit to db
    if request.method == "POST":

        # Parse & sanitize form data
        habit_data = {
            "title": request.form.get("title"),
        }
        # Create new habit object
        new_habit = Habit(
            title=habit_data["title"]
        )

        # Add new_habit to db
        session = db_session()
        try:
            session.add(new_habit)
            session.commit()
            # Display flash() for add confirmation
            flash(f"Habit added successfully.")
            return redirect(url_for("habits.dashboard")) # Redirect after POST - NOT render_template
            # Follows Post/Redirect/Get (PRG) pattern
        finally:
            session.close()
    else:
        return render_template("habits/add_habit.html")
    
# Creates a new HabitCompletion record to mark a Habit complete and enable more robust habit analytics in future
@habits_bp.route("/<int:habit_id>/completions", methods=["POST"])
def create_habit_completion(habit_id):
    
    # So we have the habit_id and need to make a new HabitCompletion entry using that as its foreignkey
    # Just have primary key and date default otherwise, so don't need to specify/add those
    new_habit_completion = HabitCompletion(
        habit_id = habit_id
    )
    session = db_session()
    try:
        session.add(new_habit_completion)
        session.commit()
        return "", 201  # 201 = Created (success for POST)
    finally:
        session.close()


# Deletes a given HabitCompletion record (acts as our "habit marked complete")
# For now, we'll only allow habits to have a single completion record in a given day
@habits_bp.route("/<int:habit_id>/completions/today", methods=["DELETE"])
def delete_habit_completion(habit_id):
    from datetime import date
    today = date.today()

    session = db_session()
    try:
        # Find corresponding habitcompletion entry for today
        habit_completion = session.query(HabitCompletion).filter(
            HabitCompletion.habit_id == habit_id,
            func.date(HabitCompletion.completed_at) == today
        ).first()

        if habit_completion:
            session.delete(habit_completion)
            session.commit()
            return "", 204
        else:
            return {"error": "No completion found for today"}, 404
        
    finally:
        session.close()