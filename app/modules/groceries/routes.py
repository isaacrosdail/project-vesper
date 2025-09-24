from flask import (Blueprint, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from flask import session as fsession

from app._infra.database import database_connection, with_db_session
from app.modules.groceries.viewmodels import ProductPresenter, TransactionPresenter, ProductViewModel, TransactionViewModel
from app.modules.groceries.pricing import get_price_per_100g
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.validators import validate_and_parse_product_data
from app.shared.middleware import set_toast

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    products = groceries_repo.get_all_products()
    transactions = groceries_repo.get_all_transactions()

    shopping_list, _ = groceries_repo.get_or_create_shoppinglist()

    for transaction in transactions:
        transaction.price_per_100g = get_price_per_100g(transaction)
    
    txn_viewmodels = [TransactionViewModel(t, current_user.timezone) for t in transactions]
    prod_viewmodels = [ProductViewModel(p, current_user.timezone) for p in products]
    ctx = {
        "products": prod_viewmodels,
        "transactions": txn_viewmodels,
        "product_headers": ProductPresenter.build_columns(),
        "transaction_headers": TransactionPresenter.build_columns(),
        "shopping_list": shopping_list
    }
    return render_template("groceries/dashboard.html", **ctx)


@groceries_bp.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        product_data = {
            "barcode": request.form.get("barcode"),
            "name": request.form.get("name"),
            "category": request.form.get("category"),
            "net_weight": float(request.form.get("net_weight", 0)),
            "unit_type": request.form.get("unit_type"),
            "calories_per_100g": request.form.get("calories_per_100g")
        }

        errors = validate_and_parse_product_data(product_data)
        if errors:
            fsession['form_data'] = request.form.to_dict() # save form_data for UX
            for e in errors:
                set_toast(e, 'error') # TODO: debug - can we handle multiple at all?
            return redirect(url_for('groceries.products'))
        
        # Handle database errors specifically
        try:
            with database_connection() as session:
                groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
                product, was_created = groceries_repo.get_or_create_product(**product_data)
                if was_created:
                    set_toast('Product added successfully', 'success')
                else:
                    set_toast('Product already exists, using existing entry', 'info')
                return redirect(url_for("groceries.dashboard"))
        except Exception as e:
            fsession['form_data'] = request.form.to_dict()
            set_toast('Something went wrong. Please try again.', 'error')
            return redirect(url_for('groceries.products'))

    else:
        return render_template("groceries/add_product.html")


@groceries_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():

    if request.method == "POST":
        with database_connection() as session:
            groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
            groceries_service = GroceriesService(groceries_repo)

            # Process form data in service
            form_data = request.form.to_dict()
            result = groceries_service.process_transaction_form(form_data)

            # Handle error(s)
            if not result['success']:
                fsession['form_data'] = form_data
                if result['error_type'] == 'product_not_found':
                    fsession['show_product_fields'] = True
                set_toast(result['message'], 'error')
                return redirect(url_for('groceries.transactions'))
            
            # Success
            set_toast(result['message'], 'success')

            # Handle action-based redirects
            action = request.form.get("action")
            if action == "submit":
                return redirect(url_for("groceries.dashboard"))
                
        return redirect(url_for("groceries.dashboard"))
    
    elif request.method == "GET":
        saved_form_data = fsession.pop('form_data', {})
        show_product_fields = fsession.pop('show_product_fields', False)
        barcode = request.args.get("barcode")
        return render_template(
            "groceries/add_transaction.html",
            barcode=barcode,
            show_product_fields=show_product_fields,
            transaction_data=saved_form_data
        )
    
@groceries_bp.route("/shopping-list/items", methods=["POST"])
@login_required
@with_db_session
def add_shoppinglist_item(session):
    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    
    data = request.get_json()
    product_id = data.get("product_id")

    item, _ = groceries_repo.add_item_to_shoppinglist(product_id)

    return jsonify({
        "success": True, 
        "message": "Added item to shopping list!",
        "item_id": item.id
    })