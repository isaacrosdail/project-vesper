## Generalized CRUD handling routes for ANY module/model
## STRONGLY consider moving to a future utils or helpers directory in future

from datetime import datetime, timezone

from app.core.database import database_connection
from app.modules.groceries.models import Product, Transaction
from app.modules.habits.models import Habit
from app.modules.tasks.models import Task
from flask import Blueprint, jsonify, request

# Blueprint registration
crud_bp = Blueprint("crud", __name__)

# Generalized PATCH, DELETE which supports:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module and subtype to resolve to the specific model of item altered
modelMap = {
    ("groceries", "product"): Product,
    ("groceries", "transaction"): Transaction,
    ("tasks", "none"): Task,
    ("habits", "none"): Habit,
}

@crud_bp.route("/<module>/<subtype>/<int:item_id>", methods=["PATCH", "DELETE"])
def item(module, subtype, item_id):

    try:
        with database_connection() as session:

            model = modelMap.get((module, subtype)) # so 'tasks', 'none' returns Task class
            item = session.get(model, item_id)

            # If item doesn't exist
            if not item:
                return jsonify({"success": False, "message": f"{model.__name__} not found."}), 404
            
            if request.method == 'PATCH':
                data = request.get_json() # get request body
                for field, value in data.items():
                    setattr(item, field, value)
                return jsonify({"success": True, "message": f"Successfully updated {model.__name__}"}), 200
            
            elif request.method == 'DELETE':
                # Products => soft delete
                if model.__name__ == 'Product':
                    item.deleted_at = datetime.now(timezone.utc)
                # All else => hard delete
                else:
                    session.delete(item)
                    
                return jsonify({"success": True, "message": f"{model.__name__} deleted"}), 200 # 200 = OK
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500 # 500 = Internal Server Error