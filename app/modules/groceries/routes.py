from decimal import Decimal

from app.core.database import database_connection
from app.modules.groceries import models as grocery_models
from app.modules.groceries import repository as grocery_repo
from app.modules.groceries.utils import get_price_per_100g
from app.utils.sorting import bubble_sort
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
def dashboard():

    try:
        with database_connection() as session:
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

            # Fetch products and transactions
            products = grocery_repo.get_all_products(session)
            transactions = grocery_repo.get_all_transactions(session)

            # Compute price_per_100g using our util function
            # Just tack that bad boy on there as a new attr
            for transaction in transactions:
                transaction.price_per_100g = get_price_per_100g(transaction)

            # Sort transactions by most recent DateTime first
            bubble_sort(transactions, 'created_at', reverse=True)
                
            return render_template(
                "groceries/dashboard.html", products = products,
                transactions = transactions, 
                product_column_names = product_column_names,
                transaction_column_names = transaction_column_names
            )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@groceries_bp.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        # Parse & sanitize form data
        product_data = {
            "barcode": request.form.get("barcode"),
            "product_name": request.form.get("product_name"),
            "category": request.form.get("category"),
            "net_weight": float(request.form.get("net_weight", 0)),
            "unit_type": request.form.get("unit_type"),
            "calories_per_100g": request.form.get("calories_per_100g")
        }

        try:
            with database_connection() as session:
                grocery_repo.get_or_create_product(session, **product_data)
                flash("Product added successfully.")    # Flash message to confirm
                return redirect(url_for("groceries.dashboard"))

        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        
    # GET => Show add_product form page
    else:
        return render_template("groceries/add_product.html")

# TODO: Clean this one up
@groceries_bp.route("/transactions", methods=["GET", "POST"])
def transactions():

    if request.method == "POST":
        # Grab form data (used for both validation and repopulating form if we need to show it again)
        form_data = request.form.to_dict()
        # Bool to conditionally determine flash() message
        # TODO: Clean this file up & determine what's needed where
        product_created = False

        ######## TODO: EXTRACT THIS VALIDATION/ETC STUFF INTO HELPER FUNCTIONS
        # Normalize
        product_data = {
            # Use .get when the field might not be included at all (eg., in our "first pass" for a non-existent product here)
            "barcode": form_data.get("barcode", "").strip(),
            "product_name": form_data.get("product_name", "").strip(),
            "net_weight": form_data.get("net_weight", "").strip(),
            "category": form_data.get("category", "").strip(),
            "unit_type": form_data.get("unit_type", "").strip(),
            "calories_per_100g": form_data.get("calories_per_100g", "").strip(),
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
        
        try:
            with database_connection() as session:
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

                flash("Transaction added successfully.") # flash confirmation

                # Redirect logic based on user action submitted
                action = request.form.get("action")
                if action == "submit":
                    return redirect(url_for("groceries.dashboard"))
                elif action == "next_item":
                    return redirect(url_for("groceries.add_transaction"))
                
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

        return redirect(url_for("groceries.dashboard"))
    # GET
    else:
        barcode = request.args.get("barcode")
        return render_template(
            "groceries/add_transaction.html",
            barcode=barcode,
            show_product_fields=False, # Don't show add_product fields like net_weight by default
            transaction_data={} # For the "first" time add_transaction to prevent "undefined transaction_data"
        ) 
