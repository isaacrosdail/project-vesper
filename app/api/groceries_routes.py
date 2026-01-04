
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import request, Response
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response, validation_failed
from app.modules.groceries.service import create_groceries_service
from app.modules.groceries.validators import (validate_product,
                                              validate_transaction)
from app.shared.decorators import login_plus_session
from app.shared.parsers import parse_product_data, parse_transaction_data


@api_bp.post("/groceries/products")
@api_bp.put("/groceries/products/<int:product_id>")
@login_plus_session
def products(session: 'Session', product_id: int | None = None) -> tuple[Response, int]:

    parsed_data = parse_product_data(request.form.to_dict())
    typed_data, errors = validate_product(parsed_data)
    if errors:
        return validation_failed(errors), 400

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    result = groceries_service.save_product(typed_data, product_id)

    if not result["success"]:
        return api_response(False, result["message"], errors=result["errors"]), 400
    
    product = result["data"]["product"]

    status_code = 201 if request.method == 'POST' else 200
    return api_response(
        True,
        result["message"],
        data = product.to_api_dict()
    ), status_code



@api_bp.post("/groceries/transactions")
@api_bp.put("/groceries/transactions/<int:transaction_id>")
@login_plus_session
def transactions(session: 'Session', transaction_id: int | None = None) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    form_data = request.form.to_dict()
    product_id_input = form_data["product_id"] # NOTE: string

    # Case A: Create new product first
    if product_id_input == '__new__':
        # 1. Validate product
        parsed_product_data = parse_product_data(form_data)
        typed_product_data, product_errors = validate_product(parsed_product_data)
        if product_errors:
            return validation_failed(product_errors), 400
        
        # 3. Call service to create product, use its id for below transaction add
        result = groceries_service.save_product(typed_product_data, product_id=None)

        if not result["success"]:
            return api_response(
                False,
                "Failed to create product",
                errors=result.get("errors")
            ), 400

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

    result = groceries_service.save_transaction(product_id, typed_transaction_data, transaction_id) # None -> POST, else PUT
    
    transaction = result["data"]["transaction"]

    status_code = 201 if request.method == 'POST' else 200
    return api_response(
        True,
        result["message"],
        data = transaction.to_api_dict()
    ), status_code



@api_bp.post("/groceries/shopping-lists/items")
@login_plus_session
def add_shoppinglist_item(session: 'Session') -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)

    data = request.get_json()
    product_id = data.get("product_id")
    quantity_wanted = data.get("quantity_wanted")

    result = groceries_service.add_item_to_shoppinglist(product_id, quantity_wanted)
    item = result["data"]["item"]
    return api_response(
        True,
        result["message"],
        data = item.to_api_dict()
    ), 201