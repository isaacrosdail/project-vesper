from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.groceries.pricing import get_price_per_100g
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.modules.groceries.viewmodels import (ProductPresenter,
                                              ProductViewModel,
                                              TransactionPresenter,
                                              TransactionViewModel)


groceries_bp = Blueprint('groceries', __name__, template_folder="templates", url_prefix="/groceries")


@groceries_bp.route("/dashboard", methods=["GET"])
@login_required
@with_db_session
def dashboard(session):

    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    products = groceries_repo.get_all_products()
    transactions = groceries_repo.get_all_transactions()

    shopping_list, _ = groceries_service.get_or_create_shoppinglist()
    
    # TODO: Should cache/store to DB column
    for transaction in transactions:
        transaction.price_per_100g = get_price_per_100g(transaction)
    
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
