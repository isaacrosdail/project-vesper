from flask import Blueprint, flash, render_template, redirect, url_for, request
from app.core.database import get_db_session
from app.modules.groceries import models as grocery_models
from app.modules.groceries import repository as grocery_repo
from decimal import Decimal

import time

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")

# Debug print
print(" groceries routes.py imported")

@groceries_bp.route("/")
def dashboard():
    print("Rendering GROCERIES dashboard")
    session = get_db_session()
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

    try:
            # Fetch products and transactions, pass into render_template
        products = grocery_repo.get_all_products(session)
        transactions = grocery_repo.get_all_transactions(session)
    finally:
        session.close()
        
    return render_template("groceries/dashboard.html", products = products,
                           transactions = transactions, 
                           product_column_names = product_column_names,
                           transaction_column_names = transaction_column_names
                        )

@groceries_bp.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        # Parse & sanitize form data
        product_data = {
            "barcode": request.form.get("barcode"),
            "product_name": request.form.get("product_name"),
            "price": Decimal(request.form.get("price", "0")),
            "net_weight": float(request.form.get("net_weight", 0))
        }
        session = get_db_session()
        try:
            grocery_repo.ensure_product_exists(session, **product_data)
            session.commit()
        finally:
            session.close()

        return redirect(url_for("groceries.dashboard"))
    else:
        return render_template("groceries/add_product.html")

@groceries_bp.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    print("Add_transaction route HIT")
    time.sleep(2)
    session = get_db_session()

    if request.method == "POST":
        action = request.form.get("action")

        # Parse & sanitize form data
        product_data = {
            "barcode": request.form.get("barcode"),
            "product_name": request.form.get("product_name"),
            "price": Decimal(request.form.get("price_at_scan", "0")),
            "net_weight": float(request.form.get("net_weight", 0)),
            "quantity": int(request.form.get("quantity") or 1)
        }

        print("lookup_barcode HIT")
        time.sleep(1)
        # Lookup barcode first
        product = grocery_repo.lookup_barcode(session, product_data["barcode"])
        if not product:
            flash("Product not found. Please add it first.")
            return redirect(url_for("groceries.add_product", barcode=product_data["barcode"]))
        
        print("logging transaction...")
        time.sleep(1)
        # Log transaction
        grocery_repo.add_transaction(session, product, price=product_data["price"], quantity=product_data["quantity"])
        session.commit()

        # Redirect accordingly
        if action == "submit":
            session.close()
            return redirect(url_for("groceries.dashboard"))
        elif action == "next_item":
            session.close()
            return redirect("/add_transaction")
    # GET
    else:
        barcode = request.args.get("barcode")
        return render_template("groceries/add_transaction.html", barcode=barcode)