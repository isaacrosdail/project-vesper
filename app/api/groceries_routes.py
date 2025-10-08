
from flask import request
from flask_login import current_user, login_required

from app.api import api_bp
from app._infra.database import with_db_session
from app.modules.groceries.repository import GroceriesRepository
from app.modules.groceries.service import GroceriesService
from app.api.responses import api_response


@api_bp.route("/groceries/shopping-lists/items", methods=["POST"])
@login_required
@with_db_session
def add_shoppinglist_item(session):
    groceries_repo = GroceriesRepository(session, current_user.id, current_user.timezone)
    groceries_service = GroceriesService(groceries_repo)

    data = request.get_json()
    product_id = data.get("product_id")
    quantity_wanted = data.get("quantity_wanted")

    item, _ = groceries_service.add_item_to_shoppinglist(product_id)

    return api_response(
        True,
        "Added item to shopping list",
        data = item.to_api_dict()
    ), 201