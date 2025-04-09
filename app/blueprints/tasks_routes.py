from flask import Blueprint, render_template, redirect, url_for, request
from app.database import get_session

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/tasks")
def tasks():
    return render_template("tasks/tasks.html")