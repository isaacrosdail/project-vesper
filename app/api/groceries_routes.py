from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Response, request
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.api import api_bp
from app.api.responses import api_response
from app.modules.groceries.schemas import (
    ProductCreate,
    ProductPatch,
    RecipeCreate,
    RecipePatch,
    ShoppingListItemCreate,
    ShoppingListItemPatch,
    TransactionPatch,
)
from app.modules.groceries.service import create_groceries_service
from app.shared.decorators import login_plus_session


@api_bp.post("/groceries/products")
@login_plus_session
def post_product(session: Session) -> tuple[Response, int]:
    validated = ProductCreate(**request.json)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    product = groceries_service.create_product(validated)
    return api_response(success=True, message="Product created", data=product.to_api_dict()), 201


@api_bp.patch("/groceries/products/<int:product_id>")
@login_plus_session
def patch_product(session: Session, product_id: int) -> tuple[Response, int]:
    validated = ProductPatch(**request.json)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    product = groceries_service.update_product(validated, product_id)
    return api_response(success=True, message="Product updated", data=product.to_api_dict()), 200



@api_bp.get("/groceries/products")
@login_plus_session
def products_list(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)

    if last_n_days:
        start_utc, end_utc = dth.last_n_days_range(last_n_days, current_user.timezone)
        results = groceries_service.product_repo.get_all_in_window(start_utc, end_utc)
    else:
        results = groceries_service.product_repo.get_all()
    data = [t.to_api_dict() for t in results]

    return api_response(success=True, message=f"Retrieved {len(results)} products", data=data), 200


@api_bp.patch("/groceries/transactions/<int:transaction_id>")
@login_plus_session
def patch_transaction(session: Session, transaction_id: int) -> tuple[Response, int]:
    validated = TransactionPatch(**request.json)
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    transaction = groceries_service.update_transaction(validated, transaction_id)
    return api_response(success=True, message="Transaction updated", data=transaction.to_api_dict()), 200

@api_bp.post("/groceries/transactions")
@login_plus_session
def create_transaction(session: Session) -> tuple[Response, int]:
    data = request.json
    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    transaction = groceries_service.create_transaction(data)
    return api_response(success=True, message="Transaction created", data=transaction.to_api_dict()), 201


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
    data = [t.to_api_dict() for t in results]

    return api_response(success=True, message=f"Retrieved {len(results)} transactions", data=data), 200


@api_bp.post("/groceries/shopping_list_items")
@login_plus_session
def post_shopping_list_item(session: Session) -> tuple[Response, int]:
    validated = ShoppingListItemCreate(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    item = groceries_service.add_item_to_shopping_list(validated.product_id, validated.quantity_wanted)
    return api_response(success=True, message="Item added to shopping list", data=item.to_api_dict()), 201

@api_bp.patch("/groceries/shopping_list_items/<int:item_id>")
@login_plus_session
def patch_shopping_list_item(session: Session, item_id: int) -> tuple[Response, int]:
    validated = ShoppingListItemPatch(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    item = groceries_service.update_shopping_list_item(item_id, validated)
    return api_response(success=True, message="Item updated", data=item.to_api_dict()), 200



@api_bp.post("/groceries/recipes")
@login_plus_session
def post_recipe(session: Session) -> tuple[Response, int]:
    validated = RecipeCreate(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    recipe = groceries_service.create_recipe(validated)
    return api_response(success=True, message="Recipe created", data=recipe.to_api_dict()), 201


@api_bp.patch("/groceries/recipes/<int:recipe_id>")
@login_plus_session
def patch_recipe(session: Session, recipe_id: int) -> tuple[Response, int]:
    validated = RecipePatch(**request.json)

    groceries_service = create_groceries_service(session, current_user.id, current_user.timezone)
    recipe = groceries_service.update_recipe(recipe_id, validated)
    return api_response(success=True, message="Recipe updated", data=recipe.to_api_dict()), 200


@api_bp.get("/groceries/recipes/<int:recipe_id>")
@login_plus_session
def get_recipe_detail(session: Session, recipe_id: int) -> tuple[Response, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    recipe = groceries_service.recipe_repo.get_recipe_with_ingredients(recipe_id)
    if not recipe:
        return api_response(success=False, message="Recipe not found"), 404

    return api_response(success=True, message="Retrieved recipe", data=recipe.to_api_dict(include_relations=True)
    ), 200


# TODO: Rough, fix
@api_bp.get("/groceries/nutrition_logs/daily_totals")
@login_plus_session
def daily_totals(session: Session) -> tuple[Response, int]:
    last_n_days = request.args.get("lastNDays", type=int)
    service = create_groceries_service(session, current_user.id, current_user.timezone)
    start, end = dth.last_n_days_range(last_n_days, current_user.timezone)
    results = service.nutrition_log_repo.get_daily_calorie_totals(start, end)

    return api_response(success=True, message="gotcha", data=results), 200
