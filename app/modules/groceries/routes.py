from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.core.database import db_session
from app.modules.groceries import models as grocery_models
from app.modules.groceries import repository as grocery_repo

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")

# Debug print
print(" groceries routes.py imported")

@groceries_bp.route("/", methods=["GET"])
def dashboard():

    session = db_session()
    try:
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

        # Sort transactions list by most recent DateTime first
        transactions.sort(key=lambda trans: trans.date_scanned, reverse=True)
            
        return render_template(
            "groceries/dashboard.html", products = products,
            transactions = transactions, 
            product_column_names = product_column_names,
            transaction_column_names = transaction_column_names
        )
    finally:
        session.close()

@groceries_bp.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        # Parse & sanitize form data
        product_data = {
            "barcode": request.form.get("barcode"),
            "product_name": request.form.get("product_name"),
            "price": Decimal(request.form.get("price", "0")),
            "net_weight": float(request.form.get("net_weight", 0))
        }
        session = db_session()
        try:
            grocery_repo.ensure_product_exists(session, **product_data)
            session.commit()
            # Flash message to confirm
            flash("Product added successfully.")

            return redirect(url_for("groceries.dashboard"))
        finally:
            session.close()
    else:
        return render_template("groceries/add_product.html")

@groceries_bp.route("/transactions/add", methods=["GET", "POST"])
def add_transaction():

    if request.method == "POST":

        # Grab form data (used for both validation and repopulating form if we need to show it again)
        form_data = request.form.to_dict()
        # Bool to conditionally determine flash() message
        product_created = False
        # Normalize
        product_data = {
            # Use .get when the field might not be included at all (eg., in our "first pass" for a non-existent product here)
            "barcode": form_data.get("barcode", "").strip(),
            "product_name": form_data.get("product_name", "").strip(),
            "net_weight": form_data.get("net_weight", "").strip()
        }
        transaction_data = {
            "price": form_data.get("price_at_scan", "").strip(),
            "quantity": form_data.get("quantity", "").strip()
        }
        # Parse
        try:
            if product_data["net_weight"]:
                product_data["net_weight"] = float(product_data["net_weight"])
            else:
                product_data["net_weight"] = None

            transaction_data["price"] = Decimal(transaction_data["price"])
            transaction_data["quantity"] = int(transaction_data["quantity"] or 1)
        except (ValueError, TypeError):
            flash("Invalid input.")
            return render_template(
                "groceries/add_transaction.html",
                show_product_fields=True,
                transaction_data=form_data # Use original form data for re-render
                )
        
        # Validate
        if not product_data["barcode"]:
            flash("Barcode is required.")
            return render_template(
                "groceries/add_transaction.html",
                show_product_fields=True,
                transaction_data=form_data
            )
        
        session = db_session()
        try:
            # Check for product existence
            product = grocery_repo.lookup_barcode(session, product_data["barcode"])
        
            # Product not found yet
            # If product is missing: Check if net_weight is filled (ie., second form submit)
            if not product:
                if product_data["net_weight"] is None:
                    # Not enough info yet - redisplay form asking for net_weight
                    flash("Product not found. Please enter net weight.")
                    return render_template(
                        "groceries/add_transaction.html",
                        show_product_fields=True,
                        transaction_data=form_data
                        )
                else:
                    # Now have enough info to add product
                    grocery_repo.add_product(session, **product_data)
                    product = grocery_repo.lookup_barcode(session, product_data["barcode"])
        
            # Product exists -> Add transaction & commit
            grocery_repo.add_transaction(session, product, **transaction_data)
            session.commit()

            # Flash message to confirm
            flash("Transaction added successfully.")

            # Redirect logic based on user action submitted
            action = request.form.get("action")
            if action == "submit":
                return redirect(url_for("groceries.dashboard"))
            elif action == "next_item":
                return redirect(url_for("groceries.add_transaction"))
        finally:
            session.close()

    # GET
    else:
        barcode = request.args.get("barcode")
        return render_template(
            "groceries/add_transaction.html",
            barcode=barcode,
            show_product_fields=False, # Don't show add_product fields like net_weight by default
            transaction_data={} # For the "first" time add_transaction to prevent "undefined transaction_data"
        ) 
    
# DELETE (Product)
@groceries_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    session = db_session()
    try:
        product = session.get(grocery_models.Product, product_id) # Grab product by id from db

        # If product doesn't exist
        if not product:
            return {"error": "Product not found."}, 404
        
        db_session.delete(product)
        db_session.commit()
        
        return "", 204     # 204 means No Content (success but nothing to return, used for DELETEs)
    finally:
        session.close()

# DELETE (Transaction)
@groceries_bp.route("/transactions/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id):
    session = db_session()

    try:
        transaction = session.get(grocery_models.Transaction, transaction_id) # Grab transaction by id from db

        # If product doesn't exist
        if not transaction:
            return {"error": "Transaction not found."}, 404
        
        db_session.delete(transaction)
        db_session.commit()
        
        return "", 204     # 204 means No Content (success but nothing to return, used for DELETEs)
    
    finally:
        session.close()