# Main Flask app -- import grocery module

from flask import Flask, redirect, url_for, render_template
import datetime
import threading  ## For now, used for running background scanner input daemon

## Database handling stuff
import core.database
from modules.groceries import models as grocery_models
from modules.scanner import scan_input ## For now, used for running background scanner input

# Display current time on splash screen
current_time = datetime.datetime.now()
time_display = current_time.strftime("%H:%M:%S")
date_display = current_time.strftime("%A, %B %d")

# Prototyping BARCODE SCANNER logic/handling
def handle_barcode(barcode):
    print(f"[Scanner] Got: {barcode}")
    grocery_models.add_product(barcode)

# Start daemon so that Vesper listens in background for a barcode to be scanned
scanner_thread = threading.Thread(
    target=lambda: scan_input.simulate_scan_loop(handle_barcode),
    daemon=True
)
scanner_thread.start()
##############

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", time_display=time_display, date_display=date_display)

@app.route("/grocery")
def grocery():
    column_names = [
        grocery_models.Product.COLUMN_LABELS.get(col, col)
        for col in grocery_models.Product.__table__.columns.keys()
    ]
    products = grocery_models.get_all_products() # Fetch products from grocery DB, then pass into render_template so our template has the info too
    return render_template("groceries/grocery.html", products = products, column_names = column_names)

@app.route("/add_product")
def add_product():
    return render_template("groceries/add_product.html")

if __name__ == "__main__":
    app.run(debug=True)