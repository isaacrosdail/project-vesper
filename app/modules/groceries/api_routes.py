from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Response, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import success_response
from app.modules.groceries.schemas import (
    CookRequest,
    ProductCreate,
    ProductPatch,
    ProductRead,
    RecipeCreate,
    RecipePatch,
    RecipeRead,
    ShoppingListItemCreate,
    ShoppingListItemPatch,
    ShoppingListItemRead,
    TransactionPatch,
    TransactionRead,
)
from app.modules.groceries.service import create_groceries_service
from app.shared.decorators import login_plus_session
from app.shared.exceptions import ServiceError


@api_bp.post("/groceries/products")
@login_plus_session
def post_product(session: Session) -> tuple[Response, int]:
    validated = ProductCreate(**request.json)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    product = groceries_service.create_product(validated)
    return success_response(message="Product created", data=ProductRead.dump(product)), 201


@api_bp.patch("/groceries/products/<int:product_id>")
@login_plus_session
def patch_product(session: Session, product_id: int) -> tuple[Response, int]:
    validated = ProductPatch(**request.json)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    product = groceries_service.update_product(validated, product_id)
    return success_response(message="Product updated", data=ProductRead.dump(product)), 200


@api_bp.get("/groceries/products")
@login_plus_session
def products_list(session: Session) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    last_n_days = request.args.get("lastNDays", type=int)
    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = groceries_service.product_repo.get_all_in_window(start_utc, end_utc)
    else:
        results = groceries_service.product_repo.get_all()
    return success_response(
        message=f"Retrieved {len(results)} products",
        data=[ProductRead.dump(p) for p in results]
    ), 200


@api_bp.get("/groceries/products/<int:product_id>")
@login_plus_session
def get_product(session: Session, product_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    product = groceries_service.get_product(product_id)
    return success_response(message="Product retrieved", data=ProductRead.dump(product)), 200


@api_bp.delete("/groceries/products/<int:product_id>")
@login_plus_session
def delete_product(session: Session, product_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    groceries_service.delete_product(product_id)
    return success_response(message="Product deleted"), 200


@api_bp.patch("/groceries/transactions/<int:transaction_id>")
@login_plus_session
def patch_transaction(session: Session, transaction_id: int) -> tuple[Response, int]:
    validated = TransactionPatch(**request.json)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    transaction = groceries_service.update_transaction(validated, transaction_id)
    return success_response(message="Transaction updated", data=TransactionRead.dump(transaction)), 200

@api_bp.post("/groceries/transactions")
@login_plus_session
def create_transaction(session: Session) -> tuple[Response, int]:
    data = request.json
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    transaction = groceries_service.create_transaction(validated)
    return success_response(message="Transaction created", data=TransactionRead.dump(transaction)), 201


@api_bp.get("/groceries/transactions")
@login_plus_session
def transactions_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)

    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = groceries_service.transaction_repo.get_all_in_window(start_utc, end_utc)
    else:
        results = groceries_service.transaction_repo.get_all()
    return success_response(
        message=f"Retrieved {len(results)} transactions",
        data=[TransactionRead.dump(t) for t in results]
    ), 200


@api_bp.get("/groceries/transactions/<int:transaction_id>")
@login_plus_session
def get_transaction(session: Session, transaction_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    transaction = groceries_service.get_transaction(transaction_id)
    return success_response(message="Transaction retrieved", data=TransactionRead.dump(transaction)), 200



@api_bp.delete("/groceries/transactions/<int:transaction_id>")
@login_plus_session
def delete_transaction(session: Session, transaction_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    groceries_service.delete_transaction(transaction_id)
    return success_response(message="Transaction deleted"), 200


@api_bp.post("/groceries/shopping_list_items")
@login_plus_session
def post_shopping_list_item(session: Session) -> tuple[Response, int]:
    validated = ShoppingListItemCreate(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    item = groceries_service.add_item_to_shopping_list(validated.product_id, validated.quantity_wanted)
    return success_response(message="Item added to shopping list", data=ShoppingListItemRead.dump(item)), 201

@api_bp.patch("/groceries/shopping_list_items/<int:item_id>")
@login_plus_session
def patch_shopping_list_item(session: Session, item_id: int) -> tuple[Response, int]:
    validated = ShoppingListItemPatch(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    item = groceries_service.update_shopping_list_item(item_id, validated)
    return success_response(message="Item updated", data=ShoppingListItemRead.dump(item)), 200


@api_bp.post("/groceries/recipes")
@login_plus_session
def post_recipe(session: Session) -> tuple[Response, int]:
    validated = RecipeCreate(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    recipe = groceries_service.create_recipe(validated)
    return success_response(message="Recipe created", data=RecipeRead.dump(recipe)), 201


@api_bp.patch("/groceries/recipes/<int:recipe_id>")
@login_plus_session
def patch_recipe(session: Session, recipe_id: int) -> tuple[Response, int]:
    validated = RecipePatch(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    recipe = groceries_service.update_recipe(recipe_id, validated)
    return success_response(message="Recipe updated", data=RecipeRead.dump(recipe)), 200


@api_bp.get("/groceries/recipes/<int:recipe_id>")
@login_plus_session
def get_recipe_detail(session: Session, recipe_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    recipe = groceries_service.recipe_repo.get_recipe_with_ingredients(recipe_id)
    if not recipe:
        raise ServiceError("Recipe not found", 404)
    return success_response(
        message="Retrieved recipe",
        data=RecipeRead.dump(recipe)
    ), 200

@api_bp.delete("/groceries/recipes/<int:recipe_id>")
@login_plus_session
def delete_recipe(session: Session, recipe_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    groceries_service.delete_recipe(recipe_id)
    return success_response(message="Recipe deleted"), 200



# TODO: Rough, fix
@api_bp.get("/groceries/nutrition_logs/daily_totals")
@login_plus_session
def daily_totals(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    service = create_groceries_service(session, current_user.id, current_user.timezone)
    start, end = dth.last_n_days_range(last_n_days, current_user.timezone)
    results = service.nutrition_log_repo.get_daily_calorie_totals(start, end)

    return success_response(message="gotcha", data=results), 200

