# Main Flask app -- import grocery module

from flask import Flask, redirect, url_for, request, render_template
import datetime
import threading  ## For now, used for running background scanner input daemon

## Database handling stuff
import core.database
from modules.groceries import models as grocery_models
from modules.scanner import scan_input ## For now, used for running background scanner input
from modules.groceries.models import Product, Transaction, get_session

import random # For dummy barcodes for now, delete later (Added 29.03.25)

# Display current time on splash screen
current_time = datetime.datetime.now()
time_display = current_time.strftime("%H:%M:%S")
date_display = current_time.strftime("%A, %B %d")

# Prototyping BARCODE SCANNER logic/handling
def handle_barcode_first(barcode):
    # print(f"[Scanner] Got: {barcode}")
    # Check if barcode is already in Product table
    session = session.get_session()
    product = session.query(Product).filter_by(barcode=barcode).first()
    session.close()

    if product:
        # Product exists -> go to Add Transaction page with pre-filled info
        return redirect(url_for("add_transaction", barcode=barcode))

    grocery_models.handle_barcode(barcode)

# Start daemon so that Vesper listens in background for a barcode to be scanned
scanner_thread = threading.Thread(
    target=lambda: scan_input.simulate_scan_loop(handle_barcode_first),
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
    # Column names for Transactions model
    transaction_column_names = [
        grocery_models.Transaction.COLUMN_LABELS.get(col, col)
        for col in grocery_models.Transaction.__table__.columns.keys()
    ]
    # Column names for Products model
    product_column_names = [
        grocery_models.Product.COLUMN_LABELS.get(col, col)
        for col in grocery_models.Product.__table__.columns.keys()
    ]

    products = grocery_models.get_all_products() # Fetch products from grocery DB, then pass into render_template so our template has the info too
    transactions = grocery_models.get_all_transactions() # Fetch transactions from grocery DB
    return render_template("groceries/grocery.html", products = products, transactions = transactions, product_column_names = product_column_names, transaction_column_names = transaction_column_names)

@app.route("/add_product", methods=["GET"])
def add_product():
    return render_template("groceries/add_product.html")

@app.route("/add_transaction", methods=["GET"])
def add_transaction():
    barcode = request.args.get("barcode")
    return render_template("groceries/add_transaction.html", barcode=barcode)

@app.route("/submit_transaction")
def submit_transaction():
    action = request.form.get("action")
    
    # Process form data
    barcode = request.form.get("barcode")

    # product_info dictionary
    product_data = {
        "product_name": request.form.get("product_name"),
        "price": request.form.get("price_at_scan"),
        "net_weight": request.form.get("net_weight"),
        "quantity": request.form.get("quantity")
    }

    grocery_models.handle_barcode(barcode, **product_data)

    # Redirect based on which button was pressed
    if action == "submit":
        return redirect("/grocery")
    elif action == "next_item":
        return redirect("/add_transaction")



# Route to save form data from add_product
@app.route('/submit_product', methods=["POST"])
def submit_product():
    name = request.form.get("product_name")
    price = request.form.get("price")

    # For dummy barcodes, delete later (29.03.25)
    barcode = str(random.randint(1, 9999))

    # Save to db
    grocery_models.handle_barcode(barcode)

    return redirect(url_for("grocery"))

if __name__ == "__main__":
    app.run(debug=True)