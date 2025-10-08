## Generalized CRUD handling routes for ANY module/model_class
import sys
from flask import abort, current_app, request
from flask_login import current_user, login_required

from app.api import api_bp
from app._infra.database import with_db_session
from app.api.responses import api_response
from app.modules.auth.service import check_item_ownership
from app.modules.groceries.models import Product, Transaction, ShoppingList, ShoppingListItem
from app.modules.habits.models import Habit, HabitCompletion, LeetCodeRecord
from app.modules.metrics.models import DailyEntry
from app.modules.tasks.models import Task
from app.modules.time_tracking.models import TimeEntry
from app.shared.database.helpers import safe_delete
from app.shared.datetime.helpers import convert_to_timezone


# Generalized PATCH, DELETE, GET which support:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module + subtype to resolve to the specific model
MODEL_CLASSES = {
    ("groceries", "products"): Product,
    ("groceries", "transactions"): Transaction,
    ("groceries", "shopping_lists"): ShoppingList,
    ("groceries", "shopping_list_items"): ShoppingListItem,
    ("tasks", "tasks"): Task,
    ("habits", "habits"): Habit,
    ("habits", "habit_completions"): HabitCompletion,
    ("habits", "leet_code_records"): LeetCodeRecord,
    ("metrics", "daily_entries"): DailyEntry,
    ("time_tracking", "time_entries"): TimeEntry,
}

def get_model_class(module, subtype: str):
    return MODEL_CLASSES.get((module, subtype))

@api_bp.route("/<module>/<subtype>/<int:item_id>", methods=["GET", "PATCH", "DELETE"])
@login_required
@with_db_session
def item(session, module, subtype, item_id):

    model_class = get_model_class(module, subtype) # so 'tasks', 'task' returns Task class
    if model_class is None:
        current_app.logger.warning(f"Unknown model for {module}, {subtype}")
        abort(404)

    item = session.get(model_class, item_id)
    if not item:
        return api_response(False, f"{model_class.__name__} not found."), 404
    
    # Ownership check
    check_item_ownership(item, current_user.id)
    
    if request.method == 'GET':
        # print(item.to_api_dict(), file=sys.stderr)
        # print(dir(item), file=sys.stderr)
        return api_response(True, f"Retrieved {item.__tablename__}", data=item.to_api_dict()), 200

    if request.method == 'PATCH':
        data = request.get_json()
        for field, value in data.items():
            setattr(item, field, value)
        return api_response(True, f"Successfully updated {model_class.__name__}"), 200
    
    elif request.method == 'DELETE':
        safe_delete(session, item)
        return api_response(True, f"{model_class.__name__} deleted"), 200