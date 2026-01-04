## Generalized CRUD handling routes for ANY module/model_class
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging
from datetime import datetime

from flask import abort, request, Response
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response
from app.modules.auth.service import check_item_ownership
from app.modules.groceries.models import (Product, ShoppingList,
                                          ShoppingListItem, Transaction)
from app.modules.habits.models import Habit, HabitCompletion, LeetCodeRecord
from app.modules.metrics.models import DailyMetrics
from app.modules.tasks.models import Task
from app.modules.time_tracking.models import TimeEntry
from app.shared.database.helpers import safe_delete
from app.shared.decorators import login_plus_session
from app.shared.hooks import PATCH_HOOKS

logger = logging.getLogger(__name__)

# Generalized PATCH, DELETE, GET which support:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module + subtype to resolve to the specific model
MODEL_CLASSES: dict[tuple[str, str], Type[Any]] = {
    ("groceries", "products"): Product,
    ("groceries", "transactions"): Transaction,
    ("groceries", "shopping_lists"): ShoppingList,
    ("groceries", "shopping_list_items"): ShoppingListItem,
    ("tasks", "tasks"): Task,
    ("habits", "habits"): Habit,
    ("habits", "habit_completions"): HabitCompletion,
    ("habits", "leet_code_records"): LeetCodeRecord,
    ("metrics", "daily_metrics"): DailyMetrics,
    ("time_tracking", "time_entries"): TimeEntry,
}

def get_model_class(module: str, subtype: str) -> Type[Any] | None:
    return MODEL_CLASSES.get((module, subtype))

@api_bp.route("/<module>/<subtype>/<int:item_id>", methods=["GET", "PATCH", "DELETE"])
@login_plus_session
def item(session: 'Session', module: str, subtype: str, item_id: int) -> tuple[Response, int]:

    model_class = get_model_class(module, subtype) # so 'tasks', 'task' returns Task class
    if model_class is None:
        logger.warning(f"Unknown model for {module}, {subtype}")
        abort(404)

    item = session.get(model_class, item_id)
    if not item:
        return api_response(False, f"{model_class.__name__} not found."), 404
    
    # Ownership check
    check_item_ownership(item, current_user.id)
    
    if request.method == 'GET':
        return api_response(True, f"Retrieved {item.__tablename__}", data=item.to_api_dict()), 200

    if request.method == 'PATCH':
        data = request.get_json()
        for field, value in data.items():
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    pass    # leave as is if not a datetime string

            setattr(item, field, value)
        session.flush()

        response_data = item.to_api_dict()

        hook = PATCH_HOOKS.get(subtype)
        if hook:
            extra_data = hook(item, data, session, current_user)
            response_data |= extra_data

        return api_response(
            True,
            f"Successfully updated {model_class.__name__}",
            data=response_data
        ), 200
    
    else:
        safe_delete(session, item)
        return api_response(True, f"{model_class.__name__} deleted", data=item.to_api_dict()), 200