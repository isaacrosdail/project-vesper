from flask import (Blueprint, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from flask import session as fsession

from app._infra.database import database_connection, with_db_session
from app.modules.api.responses import api_response
from app.modules.groceries.viewmodels import ProductPresenter, TransactionPresenter, ProductViewModel, TransactionViewModel
from app.modules.groceries.pricing import get_price_per_100g
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.validators import validate_product
from app.shared.middleware import set_toast
from app.shared.parsers import parse_product_data

groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    products = groceries_repo.get_all_products()
    transactions = groceries_repo.get_all_transactions()

    shopping_list, _ = groceries_service.get_or_create_shoppinglist()
    
    # TODO: Should cache/store to DB column
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
        with database_connection() as session:
            groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
            groceries_service = GroceriesService(groceries_repo)

            result = groceries_service.process_product_form(request.form.to_dict())

            if result["success"]:
                set_toast(result["message"], 'success')
                return redirect(url_for("groceries.dashboard"))
            else:
                fsession['form_data'] = request.form.to_dict() # save form_data for UX
                for field_errors in result["errors"].values():
                    for error in field_errors:
                        set_toast(error, 'error')
                return redirect(url_for('groceries.products'))

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
            show_product_fields = fsession.get('show_product_fields', False)

            result = groceries_service.process_transaction_form(form_data, show_product_fields)

            # Handle error(s)
            if not result['success']:
                fsession['form_data'] = form_data
                if result['data']['error_type'] == 'product_not_found':
                    fsession['show_product_fields'] = True
                set_toast(result['message'], 'error')
                return redirect(url_for('groceries.transactions'))
            
            # Success (clear flags)
            set_toast(result['message'], 'success')
            fsession.pop('show_product_fields', None)
            fsession.pop('form_data', None)

            # Handle action-based redirects
            # TODO: Scrap
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
    groceries_service = GroceriesService(groceries_repo)

    data = request.get_json()
    product_id = data.get("product_id")

    item, _ = groceries_service.add_item_to_shoppinglist(product_id)

    return api_response(
        True,
        "Added item to shopping list",
        data={
            "item_id": item.id,
            "product_id": item.product_id
        }
    ), 201