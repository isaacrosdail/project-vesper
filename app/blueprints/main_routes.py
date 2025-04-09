from flask import Blueprint, render_template

# Other imports
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    # Display current time on splash screen
    current_time = datetime.now()
    time_display = current_time.strftime("%H:%M:%S")
    date_display = current_time.strftime("%A, %B %d")
    return render_template("index.html", time_display=time_display, date_display=date_display)