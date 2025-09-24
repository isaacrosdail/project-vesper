## Generalized CRUD handling routes for ANY module/model_class

from flask import Blueprint, abort, current_app, jsonify, request
from flask_login import current_user, login_required

from app._infra.database import with_db_session
from app.modules.auth.service import check_item_ownership
from app.modules.groceries.models import Product, Transaction, ShoppingList, ShoppingListItem
from app.modules.habits.models import Habit, HabitCompletion, LeetCodeRecord
from app.modules.metrics.models import DailyEntry
from app.modules.tasks.models import Task
from app.modules.time_tracking.models import TimeEntry
from app.shared.database.helpers import safe_delete

crud_bp = Blueprint("crud", __name__)

# Generalized PATCH, DELETE which supports:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module + subtype to resolve to the specific model
MODEL_CLASSES = {
    ("groceries", "product"): Product,
    ("groceries", "transaction"): Transaction,
    ("groceries", "shopping_list"): ShoppingList,
    ("groceries", "shopping_list_item"): ShoppingListItem,
    ("tasks", "task"): Task,
    ("habits", "habit"): Habit,
    ("habits", "habit_completion"): HabitCompletion,
    ("habits", "leetcode_record"): LeetCodeRecord,
    ("metrics", "daily_entry"): DailyEntry,
    ("time_tracking", "time_entry"): TimeEntry,
}

def get_model_class(module, subtype: str):
    return MODEL_CLASSES.get((module, subtype))

@crud_bp.route("/<module>/<subtype>/<int:item_id>", methods=["PATCH", "DELETE"])
@login_required
@with_db_session
def item(session, module, subtype, item_id):

    model_class = get_model_class(module, subtype) # so 'tasks', 'task' returns Task class
    if model_class is None:
        current_app.logger.warning(f"Unknown model for {module}, {subtype}")
        abort(404)

    item = session.get(model_class, item_id)
    if not item:
        return jsonify({
            "success": False, 
            "message": f"{model_class.__name__} not found."
        }), 404
    
    # Ownership check
    check_item_ownership(item, current_user.id)
    
    if request.method == 'PATCH':
        data = request.get_json()
        for field, value in data.items():
            setattr(item, field, value)
        return jsonify({
            "success": True, 
            "message": f"Successfully updated {model_class.__name__}"
        }), 200
    
    elif request.method == 'DELETE':
        safe_delete(session, item)
        return jsonify({
            "success": True, 
            "message": f"{model_class.__name__} deleted"
        }), 200