from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Response
    from sqlalchemy.orm import Session

import io

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

import app.shared.datetime_.helpers as dth
from app.modules.groceries.models import ProductCategoryEnum, UnitEnum
from app.modules.groceries.service import create_groceries_service
from app.modules.groceries.viewmodels import (
    ProductPresenter,
    ProductViewModel,
    TransactionPresenter,
    TransactionViewModel,
)
from app.shared.decorators import login_plus_session
from app.shared.utils import set_toast

groceries_bp = Blueprint(
    "groceries", __name__, template_folder="templates", url_prefix="/groceries"
)


@groceries_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    transactions = groceries_service.transaction_repo.get_all() # TODO: this eager-loads (vs stock get_all())
    products = groceries_service.product_repo.get_all()
    transactions_for_table = [
        TransactionViewModel(t, current_user.timezone) for t in transactions
    ]

    products_for_dropdown = groceries_service.product_repo.get_all_products(
        include_soft_deleted=True
    )
    products_for_table = [
        ProductViewModel(p, current_user.timezone) for p in products
    ]

    shopping_list, _ = groceries_service.get_or_create_shopping_list()

    # TODO: For nutrition card, dbl check
    macros, meals = groceries_service.macros_summary(targets=current_user.prefs)

    # TODO: For new card on groceries, should refine/revisit ofc
    last_shopping_trip = groceries_service.shopping_trip_repo.get_most_recent_trip()
    import sys
    print(last_shopping_trip, file=sys.stderr)

    start_utc, end_utc = dth.last_n_days_range(days_ago=31, tz_str=current_user.timezone)
    top_purchased = groceries_service.transaction_repo.get_top_purchased_products(start_utc, end_utc)

    recipes = groceries_service.recipe_repo.get_all()
    ## TODO: Make this the "5 recipes for which we have the most ingredients/amount in stock for"
    ## OR: top 5 "most fitting" given our current standing as far as calories/macros for today goes?
    recipes = recipes[:5]


    ctx = {
        "transaction_headers": TransactionPresenter.build_columns(),
        "transactions_for_table": transactions_for_table,
        "products_for_dropdown": products_for_dropdown,
        "product_headers": ProductPresenter.build_columns(),
        "products_for_table": products_for_table,
        "shopping_list": shopping_list,
        "ProductCategoryEnum": ProductCategoryEnum,
        "UnitEnum": UnitEnum,
        "macros": macros,
        "meals": meals,
        "transactions": transactions, # TODO: for the new cards stuff
        "products": products,
        "last_shopping_trip": last_shopping_trip,
        "top_purchased": top_purchased,
        "recipes": recipes,
        # "targets_dict": targets_dict
    }
    return render_template("groceries/dashboard.html", **ctx), 200

@groceries_bp.get("/recipes")
@login_plus_session
def recipes(session: Session) -> tuple[str, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    shopping_list, _ = groceries_service.get_or_create_shopping_list()
    recipes = groceries_service.recipe_repo.get_all()
    products = groceries_service.product_repo.get_all_products()

    ctx = {
        "recipes": recipes,
        "products": products,
        "mass_units": UnitEnum,
        "shopping_list": shopping_list,
    }
    return render_template("groceries/recipes.html", **ctx), 200

# TODO: fix up
@groceries_bp.post("/nutrition_logs")
@login_plus_session
def nutrition_logs(session: Session) -> Response:
    file = request.files["file"]
    text_stream = io.TextIOWrapper(file, encoding="UTF-8")
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    count = groceries_service.import_nutrition_csv(text_stream)
    set_toast(f"CSV imported! Received {count} new entries", "success")

    return redirect(url_for("groceries.dashboard"))


# For our tables
@groceries_bp.get("/data")
@login_plus_session
def data(session: Session) -> tuple[str, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    transactions = groceries_service.transaction_repo.get_all() # this eager-loads (vs stock get_all())
    products = groceries_service.product_repo.get_all()
    transactions_for_table = [
        TransactionViewModel(t, current_user.timezone) for t in transactions
    ]

    products_for_dropdown = groceries_service.product_repo.get_all_products(
        include_soft_deleted=True
    )
    products_for_table = [
        ProductViewModel(p, current_user.timezone) for p in products
    ]

    ctx = {
        "transactions_for_table": transactions_for_table,
        "products_for_dropdown": products_for_dropdown,
        "products_for_table": products_for_table,
        "transaction_headers": TransactionPresenter.build_columns(),
        "product_headers": ProductPresenter.build_columns()

    }
    return render_template("groceries/data.html", **ctx), 200
