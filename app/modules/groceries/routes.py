
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, render_template
from flask_login import current_user

from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.viewmodels import (ProductPresenter,
                                              ProductViewModel,
                                              TransactionPresenter,
                                              TransactionViewModel)
from app.shared.decorators import login_plus_session


groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_plus_session
def dashboard(session: 'Session') -> Any:

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    products = groceries_repo.get_all_products()
    transactions = groceries_repo.get_all_transactions()

    shopping_list, _ = groceries_service.get_or_create_shoppinglist()
    
    txn_viewmodels = [TransactionViewModel(t, current_user.timezone) for t in transactions]
    prod_viewmodels = [ProductViewModel(p, current_user.timezone) for p in products]
    ctx = {
        "products_list": products,
        "products": prod_viewmodels,
        "transactions": txn_viewmodels,
        "product_headers": ProductPresenter.build_columns(),
        "transaction_headers": TransactionPresenter.build_columns(),
        "shopping_list": shopping_list
    }
    return render_template("groceries/dashboard.html", **ctx)
