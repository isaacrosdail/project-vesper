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
# from app.modules.groceries.viewmodels import (
#     RecipeSlotViewModel,
# )
from app.shared.decorators import login_plus_session
from app.shared.utils import ToastType, set_toast

groceries_bp = Blueprint(
    "groceries", __name__, template_folder="templates", url_prefix="/groceries"
)


@groceries_bp.get("/dashboard")
@login_plus_session
def dashboard(session: Session) -> tuple[str, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )
    products_for_dropdown = groceries_service.product_repo.get_all_products(
        include_soft_deleted=True
    )
    ctx = {
        "products_for_dropdown": products_for_dropdown,
        "ProductCategoryEnum": ProductCategoryEnum,
        "UnitEnum": UnitEnum,
    }
    return render_template("groceries/dashboard.html", **ctx), 200

@groceries_bp.get("/recipes")
@login_plus_session
def recipes(session: Session) -> tuple[str, int]:
    return render_template("groceries/recipes.html"), 200

@groceries_bp.get("/shopping")
@login_plus_session
def shopping(session: Session) -> tuple[str, int]:
    return render_template("/groceries/shopping.html"), 200

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
    set_toast("CSV imported", f"Received {count} new entries", ToastType.SUCCESS)

    return redirect(url_for("groceries.data"))


# For our tables
@groceries_bp.get("/data")
@login_plus_session
def data(session: Session) -> tuple[str, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )

    products_for_dropdown = groceries_service.product_repo.get_all_products(
        include_soft_deleted=True
    )

    ctx = {
        "products_for_dropdown": products_for_dropdown,
    }
    return render_template("groceries/data.html", **ctx), 200
