## Generalized CRUD handling routes for ANY module/model :P
## STRONGLY consider moving to a future utils or helpers directory in future

from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from app.core.database import db_session

# Import models
from app.modules.groceries import models as grocery_models
from app.modules.tasks import models as tasks_models

# right?
crud_bp = Blueprint("crud", __name__)

### Generalizing to be able to support all CRUD ops through one generalized engine that supports:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module and subtype to resolve to the specific model of item altered
modelMap = {
    ("groceries", "product"): grocery_models.Product,
    ("groceries", "transaction"): grocery_models.Transaction,
    ("tasks", "none"): tasks_models.Task,
}

# ADD
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

        # Create item dynamically based on the model
        item = model(**data)
        db_session.add(item)
        db_session.commit()

        return redirect(url_for(f"{module}.dashboard")) # Redirect after to corresponding dashboard template


# DELETE
@crud_bp.route("/<module>/<subtype>/<int:item_id>", methods=["DELETE"])
def delete_item(module, subtype, item_id):
    session = db_session()

    # Get correct model
    model = modelMap.get((module, subtype))
    print(model)
    item = session.get(model, item_id) # Grab item by id from db

    # If item doesn't exist
    if not item:
        return {"error": f"{model.__name__} not found."}, 404
    
    db_session.delete(item)
    db_session.commit()
    
    return "", 204     # 204 means No Content (success but nothing to return, used for DELETEs)