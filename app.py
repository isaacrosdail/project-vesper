# Main Flask app -- import grocery module

from flask import Flask, redirect, url_for, request, render_template
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
    # Column names for Products model
    column_names1 = [
        grocery_models.Product.COLUMN_LABELS.get(col, col)
        for col in grocery_models.Product.__table__.columns.keys()
    ]
    # Column names for Transactions model
    column_names2 = [
        grocery_models.Transaction.COLUMN_LABELS.get(col, col)
        for col in grocery_models.Transaction.__table__.columns.keys()
    ]
    products = grocery_models.get_all_products() # Fetch products from grocery DB, then pass into render_template so our template has the info too
    transactions = grocery_models.get_all_transactions() # Fetch transactions from grocery DB
    return render_template("groceries/grocery.html", products = products, transactions = transactions, column_names1 = column_names1, column_names2 = column_names2)

@app.route("/add_product", methods=["GET"])
def add_product():
    return render_template("groceries/add_product.html")

# Route to save form data from add_product
@app.route('/submit', methods=["POST"])
def submit_product():
    name = request.form.get("product_name")
    price = request.form.get("price")

    # Save to db
    grocery_models.add_product(111, name, price)

    return redirect(url_for("grocery"))

if __name__ == "__main__":
    app.run(debug=True)