
from flask import request
from flask_login import current_user, login_required

from app.api import api_bp
from app._infra.database import with_db_session
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.api.responses import api_response, validation_failed
from app.modules.groceries.validators import (validate_barcode,
                                              validate_product,
                                              validate_transaction)
from app.shared.parsers import (parse_barcode, parse_product_data,
                                parse_transaction_data)


@api_bp.route("/groceries/products", methods=["POST"])
@api_bp.route("/groceries/products/<int:product_id>", methods=["PUT"])
@login_required
@with_db_session
def products(session, product_id=None):

    parsed_data = parse_product_data(request.form.to_dict())
    typed_data, errors = validate_product(parsed_data)
    if errors:
        return validation_failed(errors), 400

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)
    result = groceries_service.save_product(typed_data, product_id)

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"])
    
    product = result["data"]["product"]
    return api_response(
        True,
        result["message"],
        data = product.to_api_dict()
    ), 201



@api_bp.route("/groceries/transactions", methods=["POST"])
@api_bp.route("/groceries/transactions/<int:transaction_id>", methods=["PUT"])
@login_required
@with_db_session
def transactions(session, transaction_id=None):
    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)
    form_data = request.form.to_dict()
    product_id_input = form_data.get("product_id") # NOTE: string

    # Case A: Create new product first
    if product_id_input == '__new__':
        # 1. Validate product
        parsed_product_data = parse_product_data(form_data)
        typed_product_data, product_errors = validate_product(parsed_product_data)
        if product_errors:
            return validation_failed(product_errors), 400
        
        # 3. Call service to create product, use its id for below transaction add
        result = groceries_service.save_product(typed_product_data, product_id=None)

        # TODO: Implement failure of product creation response
        if not result["success"]:
            pass
        product_id = result['data']['product'].id # NOTE: now it's an int - fix?
    # Convert str from form to int
    else:
        product_id = int(product_id_input)

    # Case B (fall through): Use existing product, create transaction only
    # 1. Validate transaction
    parsed_transaction_data = parse_transaction_data(form_data)
    typed_transaction_data, transaction_errors = validate_transaction(parsed_transaction_data)
    if transaction_errors:
        return validation_failed(transaction_errors), 400

    # 2. Call service to create transaction
    result = groceries_service.save_transaction(product_id, typed_transaction_data, transaction_id) # None -> POST, else PUT
    
    transaction = result["data"]["transaction"]
    return api_response(
        True,
        result["message"],
        data = transaction.to_api_dict()
    ), 201



@api_bp.route("/groceries/shopping-lists/items", methods=["POST"])
@login_required
@with_db_session
def add_shoppinglist_item(session):
    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    data = request.get_json()
    product_id = data.get("product_id")
    quantity_wanted = data.get("quantity_wanted")

    item, _ = groceries_service.add_item_to_shoppinglist(product_id)

    return api_response(
        True,
        "Added item to shopping list",
        data = item.to_api_dict()
    ), 201