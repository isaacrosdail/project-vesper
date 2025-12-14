
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template, request
from flask_login import current_user

from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.viewmodels import (ProductPresenter,
                                              ProductViewModel,
                                              TransactionPresenter,
                                              TransactionViewModel)
from app.shared.datetime.helpers import last_n_days_range
from app.shared.decorators import login_plus_session
from app.shared.collections import sort_by_field
from app.shared.parsers import get_table_params


groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    transactions_params = get_table_params('transactions', 'created_at')
    start_utc, end_utc = last_n_days_range(transactions_params['range'], current_user.timezone)
    transactions = groceries_repo.get_all_transactions_in_window(start_utc, end_utc)
    transactions = sort_by_field(transactions, transactions_params['sort_by'], transactions_params['order'])
    txn_viewmodels = [TransactionViewModel(t, current_user.timezone) for t in transactions]

    products_params = get_table_params('products', 'name')
    start_utc, end_utc = last_n_days_range(products_params['range'], current_user.timezone)
    products = groceries_repo.get_all_products_in_window(start_utc, end_utc)
    products = sort_by_field(products, products_params['sort_by'], products_params['order'])
    prod_viewmodels = [ProductViewModel(p, current_user.timezone) for p in products]

    shopping_list, _ = groceries_service.get_or_create_shoppinglist()

    ctx = {
        "transactions_params": transactions_params,
        "transaction_headers": TransactionPresenter.build_columns(),
        "transactions": txn_viewmodels,
        "txn_form_products_list": products,
        "products_params": products_params,
        "product_headers": ProductPresenter.build_columns(),
        "products": prod_viewmodels,
        "shopping_list": shopping_list,
    }
    return render_template("groceries/dashboard.html", **ctx)
