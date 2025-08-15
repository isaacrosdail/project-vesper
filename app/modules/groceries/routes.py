import sys

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from app._infra.database import database_connection
from app.modules.groceries.models import Product, Transaction
from app.modules.groceries.pricing import get_price_per_100g
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.validators import validate_product_data
from app.shared.sorting import bubble_sort

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    try:
        with database_connection() as session:
            # TODO: build_columns() Column names for Transactions model
            transaction_headers = [
                Transaction.COLUMN_LABELS.get(col, col)
                for col in Transaction.__table__.columns.keys()
            ]
            # Column names for Products model
            product_headers = [
                Product.COLUMN_LABELS.get(col, col)
                for col in Product.__table__.columns.keys()
            ]

            # Fetch products and transactions
            groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
            products = groceries_repo.get_all_products()
            transactions = groceries_repo.get_all_transactions()

            # Compute price_per_100g using our util function => add as new attribute! Thanks SQLAlchemy
            # TODO: MINOR: Fold this into an instance method for Transaction model?
            for transaction in transactions:
                transaction.price_per_100g = get_price_per_100g(transaction)

            # Sort transactions by most recent DateTime first
            bubble_sort(transactions, 'created_at', reverse=True)
            
            ctx = {
                "products": products,
                "transactions": transactions,
                "product_headers": product_headers,
                "transaction_headers": transaction_headers,
            }
            return render_template(
                "groceries/dashboard.html", **ctx)
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
                "name": request.form.get("name"),
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
                groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
                groceries_repo.get_or_create_product(**product_data)
                flash("Product added successfully.")
                return redirect(url_for("groceries.dashboard"))
            
        else:
            return render_template("groceries/add_product.html")
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# TODO: This is god-awful
@groceries_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    try:
        if request.method == "POST":
            with database_connection() as session:
                groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
                groceries_service = GroceriesService(groceries_repo)

                # Process form data in service
                form_data = request.form.to_dict()
                result = groceries_service.process_transaction_form(form_data)
                print(f"ALPHA 2.5: error={not result['success']}", file=sys.stderr)

                # Handle error(s)
                if not result['success']:
                    flash(result['message'])
                    return render_template(
                        "groceries/add_transaction.html",
                        show_product_fields=result['show_product_fields'],
                        transaction_data=result['form_data']
                    )
                
                # Success
                flash(result['message'])
                print("Transaction added!!!", file=sys.stderr)

                # TODO: Move next_item to being a checkbox, not its own button
                # Handle action-based redirects
                action = request.form.get("action")
                if action == "submit":
                    return redirect(url_for("groceries.dashboard"))
                elif action == "next_item":
                    return redirect(url_for("groceries.add_transaction"))
                    
            return redirect(url_for("groceries.dashboard"))
        
        elif request.method == "GET":
            barcode = request.args.get("barcode")
            return render_template(
                "groceries/add_transaction.html",
                barcode=barcode,
                show_product_fields=False, # Hide product fields to start
                transaction_data={} # For the "first" time add_transaction to prevent "undefined transaction_data"
            )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500