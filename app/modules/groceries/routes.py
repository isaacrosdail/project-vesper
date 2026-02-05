from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.groceries.service import create_groceries_service
from app.modules.groceries.viewmodels import (
    ProductPresenter,
    ProductViewModel,
    TransactionPresenter,
    TransactionViewModel,
)
from app.shared.utils import sort_by_field
from app.shared.datetime_.helpers import last_n_days_range
from app.shared.decorators import login_plus_session
from app.shared.utils import get_table_params

groceries_bp = Blueprint(
    "groceries", __name__, template_folder="templates", url_prefix="/groceries"
)


@groceries_bp.get("/dashboard")
@login_plus_session
def dashboard(session: "Session") -> tuple[str, int]:
    groceries_service = create_groceries_service(
        session, current_user.id, current_user.timezone
    )

    transactions_params = get_table_params("transactions", "created_at")
    start_utc, end_utc = last_n_days_range(
        transactions_params["range"], current_user.timezone
    )
    transactions = groceries_service.transaction_repo.get_all_transactions_in_window(
        start_utc, end_utc
    )
    transactions = sort_by_field(
        transactions, transactions_params["sort_by"], transactions_params["order"]
    )
    transactions_for_table = [
        TransactionViewModel(t, current_user.timezone) for t in transactions
    ]

    products_params = get_table_params("products", "name")
    start_utc, end_utc = last_n_days_range(
        products_params["range"], current_user.timezone
    )

    products_for_dropdown = groceries_service.product_repo.get_all_products(
        include_soft_deleted=True
    )
    products_for_dropdown = sort_by_field(products_for_dropdown, "name", "asc")

    active_products_for_table = (
        groceries_service.product_repo.get_all_products_in_window(start_utc, end_utc)
    )
    active_products_for_table = sort_by_field(
        active_products_for_table, products_params["sort_by"], products_params["order"]
    )

    products_for_table = [
        ProductViewModel(p, current_user.timezone) for p in active_products_for_table
    ]

    shopping_list, _ = groceries_service.get_or_create_shoppinglist()

    category_options = [
        {"value": enum_member.value.lower(), "text": display_string}
        for enum_member, display_string in ProductViewModel.CATEGORY_LABELS.items()
    ]

    ctx = {
        "d_transactions_params": transactions_params,
        "l_transaction_headers": TransactionPresenter.build_columns(),
        "l_transactions_for_table": transactions_for_table,
        "l_products_for_dropdown": products_for_dropdown,
        "d_products_params": products_params,
        "l_product_headers": ProductPresenter.build_columns(),
        "l_products_for_table": products_for_table,
        "o_shopping_list": shopping_list,
        "l_category_options": category_options,
    }
    return render_template("groceries/dashboard.html", **ctx), 200
