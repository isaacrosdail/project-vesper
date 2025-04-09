# Main Flask app -- import grocery module
from app import create_app

# Import Blueprints for routes
from app.blueprints.grocery_routes import grocery_bp

## OLDER IMPORTS
from flask import Flask, redirect, url_for, request, render_template
import datetime
import threading  ## For now, used for running background scanner input daemon



## Database handling stuff
import core.database
from app.modules.groceries import models as grocery_models
from app.modules.groceries import repository as grocery_repo
from app.modules.scanner import scan_input ## For now, used for running background scanner input
from app.modules.groceries.models import get_session
from decimal import Decimal

import random # For dummy barcodes for now, delete later (Added 29.03.25)

# Prototyping BARCODE SCANNER logic/handling
def handle_barcode_first(barcode):
    session = session.get_session()
    try:
        result = grocery_repo.handle_barcode(session, barcode)

        if result == "added_transaction":
            session.commit()
            return
        elif result == "new_product":
            session.close()
            # Redirect to 
        
        grocery_repo.handle_barcode(barcode)
        session.commit()
    finally:
        session.close()

# Start daemon to listen in background for barcode(s)
scanner_thread = threading.Thread(
    target=lambda: scan_input.simulate_scan_loop(handle_barcode_first),
    daemon=True
)
scanner_thread.start()
# # # # #

app = create_app()

@app.route("/")
def home():
    # Display current time on splash screen
    current_time = datetime.datetime.now()
    time_display = current_time.strftime("%H:%M:%S")
    date_display = current_time.strftime("%A, %B %d")
    return render_template("index.html", time_display=time_display, date_display=date_display)


if __name__ == "__main__":
    app.run(debug=True)