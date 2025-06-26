## Generalized CRUD handling routes for ANY module/model :P
## STRONGLY consider moving to a future utils or helpers directory in future

from flask import Blueprint, redirect, render_template, request, url_for, jsonify

from app.core.database import db_session, database_connection
# Import models
from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models
from app.modules.habits.models import Habit

from datetime import datetime, timezone

# Blueprint registration
crud_bp = Blueprint("crud", __name__)

### Generalizing to be able to support all CRUD ops to handle:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module and subtype to resolve to the specific model of item altered
modelMap = {
    ("groceries", "product"): grocery_models.Product,
    ("groceries", "transaction"): grocery_models.Transaction,
    ("tasks", "none"): tasks_models.Task,
    ("habits", "none"): Habit,
}

'''
# ADD - Need to confirm whether I'm using this
@crud_bp.route("/<module>/<subtype>", methods=["GET", "POST"])
def add_item(module, subtype):
    if request.method == "GET":
        # Render correct template dynamically
        return render_template(f"{module}/add_{subtype}.html")
    
    elif request.method == "POST":
        # Handle form submission for creating new item
        model = modelMap.get((module, subtype))
        if not model:
            return {"error": "Invalid module or subtype"}, 400 # 400 Invalid input

        # Extract form data (from HTML form submission for new_[item])
        # If the form contains fields like title, type, and is_anchor,
        # this will create a dictionary like:
        # {"title": "Task Title", "type": "Feature", "is_anchor": "True"}
        data = request.form.to_dict() # originally used specific fields like request.form.get("title")

        session = db_session()
        try:
            # Create item dynamically based on the model
            item = model(**data)
            db_session.add(item)
            db_session.commit()

            return redirect(url_for(f"{module}.dashboard")) # Redirect after to corresponding dashboard template
        
        finally:
            session.close()

'''

# UPDATE (PATCH) - Trying out a generic PATCH route for editTableField
@crud_bp.route("/<module>/<subtype>/<int:item_id>", methods=["PATCH"])
def patch_item(module, subtype, item_id):

    try:
        with database_connection() as session:
            model = modelMap.get((module, subtype)) # so 'tasks', 'none' returns Task class
            item = session.get(model, item_id)

            # If item doesn't exist
            if not item:
                return jsonify({"success": False, "message": f"{model.__name__} not found."}), 404
            
            data = request.get_json() # get request body
            for field, value in data.items():
                setattr(item, field, value)

            return jsonify({"success": True, "message": f"Successfully updated {model.__name__}"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to update {model.__name__}"}), 500    


# DELETE
@crud_bp.route("/<module>/<subtype>/<int:item_id>", methods=["DELETE"])
def delete_item(module, subtype, item_id):
    session = db_session()

    try:
        with database_connection() as session:
            model = modelMap.get((module, subtype))  # Get correct model
            item = session.get(model, item_id)       # Grab item by id from db

            # If item doesn't exist
            if not item:
                return jsonify({"success": False, "message": f"{model.__name__} not found."}), 404
            
            # Soft deletes for Products, hard delete for all else
            if model.__name__ == 'Product':
                item.deleted_at = datetime.now(timezone.utc)
            else:
                session.delete(item)

            return jsonify({"success": True, "message": f"{model.__name__} deleted"}), 200 # 200 = OK
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500 # 500 = Internal Server Error