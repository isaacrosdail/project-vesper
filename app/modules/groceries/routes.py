
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
from app.shared.decorators import login_plus_session
from app.shared.collections import sort_by_field


groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:

    transactions_sort = request.args.get("transactions_sort", "created_at")
    transactions_order = request.args.get("transactions_order", "desc")
    products_sort = request.args.get("products_sort", "name")
    products_order = request.args.get("products_order", "desc")

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    products = groceries_repo.get_all_products()
    transactions = groceries_repo.get_all_transactions()

    products = sort_by_field(products, products_sort, products_order)
    transactions = sort_by_field(transactions, transactions_sort, transactions_order)

    shopping_list, _ = groceries_service.get_or_create_shoppinglist()
    
    txn_viewmodels = [TransactionViewModel(t, current_user.timezone) for t in transactions]
    prod_viewmodels = [ProductViewModel(p, current_user.timezone) for p in products]
    ctx = {
        "txn_form_products_list": products,
        "products": prod_viewmodels,
        "transactions": txn_viewmodels,
        "product_headers": ProductPresenter.build_columns(),
        "transaction_headers": TransactionPresenter.build_columns(),
        "shopping_list": shopping_list,
        "transactions_sort": transactions_sort,
        "transactions_order": transactions_order,
        "products_sort": products_sort,
        "products_order": products_order,
    }
    return render_template("groceries/dashboard.html", **ctx)
