from flask import Blueprint, jsonify, redirect, render_template, request
from flask import session as fsession
from flask import url_for
from flask_login import current_user, login_required

from app._infra.database import database_connection, with_db_session
from app.modules.api.responses import api_response
from app.modules.groceries.pricing import get_price_per_100g
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.validators import (validate_barcode,
                                              validate_product,
                                              validate_transaction)
from app.modules.groceries.viewmodels import (ProductPresenter,
                                              ProductViewModel,
                                              TransactionPresenter,
                                              TransactionViewModel)
from app.shared.middleware import set_toast
from app.shared.parsers import (parse_barcode, parse_product_data,
                                parse_transaction_data)


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

            parsed_data = parse_product_data(request.form.to_dict())
            typed_data, errors = validate_product(parsed_data)

            if errors:
                fsession['form_data'] = request.form.to_dict() # save form_data for UX
                for field_errors in result["errors"].values():
                    for error in field_errors:
                        set_toast(error, 'error')
                return redirect(url_for('groceries.products'))


            groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
            groceries_service = GroceriesService(groceries_repo)
            result = groceries_service.create_product(typed_data)

            if result["success"]:
                set_toast(result["message"], 'success')
                return redirect(url_for("groceries.dashboard"))


    return render_template("groceries/add_product.html")


@groceries_bp.route("/transactions", methods=["GET", "POST"])
@login_required
@with_db_session
def transactions(session):
    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    if request.method == "POST":
            groceries_service = GroceriesService(groceries_repo)
            form_data = request.form.to_dict()
            product_id = form_data.get("product_id")

            # Case A: Create new product first
            if product_id == '__new__':
                # 1. Validate product
                parsed_product_data = parse_product_data(form_data)
                typed_product_data, product_errors = validate_product(parsed_product_data)
                if product_errors:
                    fsession['form_data'] = form_data
                    # fsession['product_id'] = '__new__' # so we know to show
                    for field_errors in product_errors.values():
                        for error in field_errors:
                            set_toast(error, 'error')
                    return redirect(url_for('groceries.transactions'))
                
                # 3. Call service to create product, use its id for below transaction add
                result = groceries_service.create_product(typed_product_data)
                product_id = result['data']['product'].id

            # Case B (fall through): Use existing product, create transaction only
            # 1. Validate transaction
            parsed_transaction_data = parse_transaction_data(form_data)
            typed_transaction_data, transaction_errors = validate_transaction(parsed_transaction_data)
            if transaction_errors:
                fsession['form_data'] = form_data
                for field_errors in transaction_errors.values():
                    for error in field_errors:
                        set_toast(error, 'error')
                return redirect(url_for('groceries.transactions'))

            # 2. Call service to create transaction
            result = groceries_service.create_transaction(product_id, typed_transaction_data)

            set_toast(result['message'], 'success')
            return redirect(url_for('groceries.dashboard'))

    # GET
    # Need to now grab products to populate dropdown
    products = groceries_repo.get_all_products()

    saved_form_data = fsession.pop('form_data', {})
    return render_template(
        "groceries/add_transaction.html",
        products=products,
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