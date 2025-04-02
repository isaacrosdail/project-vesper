# Main Flask app -- import grocery module

from flask import Flask, redirect, url_for, request, render_template
import datetime
import threading  ## For now, used for running background scanner input daemon

## Database handling stuff
import core.database
from modules.groceries import models as grocery_models
from modules.groceries import repository as grocery_repo
from modules.scanner import scan_input ## For now, used for running background scanner input
from modules.groceries.models import get_session
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

app = Flask(__name__)

@app.route("/")
def home():
    # Display current time on splash screen
    current_time = datetime.datetime.now()
    time_display = current_time.strftime("%H:%M:%S")
    date_display = current_time.strftime("%A, %B %d")
    return render_template("index.html", time_display=time_display, date_display=date_display)

@app.route("/grocery")
def grocery():
    session = get_session()
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

    # Fetch products and transactions, pass into render_template
    products = grocery_repo.get_all_products(session)
    transactions = grocery_repo.get_all_transactions(session)
    return render_template("groceries/grocery.html", products = products,
                           transactions = transactions, 
                           product_column_names = product_column_names,
                           transaction_column_names = transaction_column_names
                        )

@app.route("/add_product", methods=["GET"])
def add_product():
    return render_template("groceries/add_product.html")

@app.route("/add_transaction", methods=["GET"])
def add_transaction():
    barcode = request.args.get("barcode")
    return render_template("groceries/add_transaction.html", barcode=barcode)

@app.route("/submit_transaction", methods=["POST"])
def submit_transaction():
    action = request.form.get("action")

    # Parse & sanitize form data
    product_data = {
        "barcode": request.form.get("barcode"),
        "product_name": request.form.get("product_name"),
        "price": Decimal(request.form.get("price_at_scan", "0")),
        "net_weight": float(request.form.get("net_weight", 0)),
        "quantity": int(request.form.get("quantity") or 1)
    }

    session = get_session()
    try:
        grocery_repo.ensure_product_exists(session, **product_data)
        product = grocery_repo.lookup_barcode(session, product_data["barcode"])
        grocery_repo.add_transaction(session, product, **product_data)
        # grocery_repo.handle_barcode(session, barcode, **product_data)
        session.commit()
    finally:
        session.close()

    # Redirect accordingly
    if action == "submit":
        return redirect("/grocery")
    elif action == "next_item":
        return redirect("/add_transaction")


# Route to save form data from add_product
@app.route('/submit_product', methods=["POST"])
def submit_product():
    barcode = request.form.get("barcode")

    # Parse & sanitize form data
    product_data = {
        "barcode": request.form.get("barcode"),
        "product_name": request.form.get("product_name"),
        "price": Decimal(request.form.get("price", "0")),
        "net_weight": float(request.form.get("net_weight", 0))
    }

    session = get_session()
    try:
        grocery_repo.ensure_product_exists(session, **product_data)
        session.commit()
    finally:
        session.close()

    return redirect(url_for("grocery"))

if __name__ == "__main__":
    app.run(debug=True)