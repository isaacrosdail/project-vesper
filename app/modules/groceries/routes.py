from app.common.sorting import bubble_sort
from app.core.database import database_connection
from app.modules.groceries.models import Product, Transaction
from app.modules.groceries import repository as grocery_repo
from app.modules.groceries.utils import get_price_per_100g
from app.modules.groceries.validate import (parse_and_validate_form_data,
                                            validate_product_data)
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    try:
        with database_connection() as session:
            # Column names for Transactions model
            transaction_column_names = [
                Transaction.COLUMN_LABELS.get(col, col)
                for col in Transaction.__table__.columns.keys()
            ]
            # Column names for Products model
            product_column_names = [
                Product.COLUMN_LABELS.get(col, col)
                for col in Product.__table__.columns.keys()
            ]

            # Fetch products and transactions
            products = grocery_repo.get_user_products(session, current_user.id)
            transactions = grocery_repo.get_user_transactions(session, current_user.id)

            # Compute price_per_100g using our util function => add as new attribute! Thanks SQLAlchemy
            # TODO: Can I fold this into an instance method for Transaction model?
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
@login_required
def products():
    try:
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

            # Validate
            errors = validate_product_data(product_data)
            if errors:
                for e in errors:
                    flash(e, "error")
                return redirect(url_for('groceries.products')) # back to form if errors

            with database_connection() as session:
                grocery_repo.get_or_create_product(session, current_user.id, **product_data)
                flash("Product added successfully.")    # Flash message to confirm
                return redirect(url_for("groceries.dashboard"))
            
        # GET => Show add_product form page
        else:
            return render_template("groceries/add_product.html")
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# TODO: Clean this one up
@groceries_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():

    try:
        if request.method == "POST":
            # Grab form data (used for both validation and repopulating form if we need to show it again)
            form_data = request.form.to_dict()

            product_data, transaction_data, error = parse_and_validate_form_data(form_data)
            if error:
                flash(error)
                return render_template(
                    "groceries/add_transaction.html",
                    show_product_fields=True,
                    transaction_data=form_data
                )
            
            with database_connection() as session:
                # Check for product existence
                product = grocery_repo.lookup_barcode(session, product_data["barcode"], current_user.id)
            
                # Product not found yet: Check if net_weight is filled (ie., second form submit)
                # Early return to form page if empty
                if not product and product_data["net_weight"] is None:
                    # Not enough info yet - redisplay form asking for net_weight
                    flash("Product not found. Please enter net weight.")
                    return render_template(
                        "groceries/add_transaction.html",
                        show_product_fields=True,
                        transaction_data=form_data
                        )
                # Have enough info => add product
                if not product:
                    grocery_repo.add_product(session, current_user.id, **product_data)
                    session.flush() # Forces INSERT without committing (context manager wouldn't have done this yet)
                    product = grocery_repo.lookup_barcode(session, product_data["barcode"], current_user.id)
            
                # Product exists -> Add transaction
                grocery_repo.add_transaction(session, product, current_user.id, **transaction_data)
                flash("Transaction added successfully.") # flash confirmation

                # Redirect logic based on user action submitted
                action = request.form.get("action")
                if action == "submit":
                    return redirect(url_for("groceries.dashboard"))
                elif action == "next_item":
                    return redirect(url_for("groceries.add_transaction"))
                    
            return redirect(url_for("groceries.dashboard"))
        
        # GET => show form
        else:
            barcode = request.args.get("barcode")
            return render_template(
                "groceries/add_transaction.html",
                barcode=barcode,
                show_product_fields=False, # By default, don't show product-relevant fields at first
                transaction_data={} # For the "first" time add_transaction to prevent "undefined transaction_data"
            ) 

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500