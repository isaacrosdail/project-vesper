## Generalized CRUD handling routes for ANY module/model_class
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

import logging
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime

from flask import Response, abort, request
from flask_login import current_user

from app.api import api_bp
from app.api.responses import api_response
from app.modules.auth.models import UnitSystemEnum
from app.modules.auth.service import check_item_ownership
from app.modules.groceries.models import (
    Product,
    ShoppingList,
    ShoppingListItem,
    Transaction,
    Recipe,
    RecipeIngredient,
)
from app.modules.habits.models import Habit, HabitCompletion, LeetCodeRecord
from app.modules.metrics.models import DailyMetrics
from app.modules.tasks.models import Task
from app.modules.time_tracking.models import TimeEntry
from app.shared.utils import kg_to_lbs
from app.shared.database.helpers import safe_delete
from app.shared.decorators import login_plus_session
from app.shared.hooks import PATCH_HOOKS

logger = logging.getLogger(__name__)

# Generalized PATCH, DELETE, GET which support:
# 1. Any number of modules (eg, groceries, tasks, etc.)
# 2. Any number of sub-models within each (eg, grocery product, grocery transaction)

# Map to correct model based on module passed in
# This uses module + subtype to resolve to the specific model
# NOTE: Using dataclass for learning, tuple keys would be simpler here
@dataclass(frozen=True)
class ModelKey:
    module: str
    subtype: str

MODEL_CLASSES: dict[ModelKey, type[Any]] = {
    ModelKey("groceries", "products"): Product,
    ModelKey("groceries", "transactions"): Transaction,
    ModelKey("groceries", "shopping_lists"): ShoppingList,
    ModelKey("groceries", "shopping_list_items"): ShoppingListItem,
    ModelKey("groceries", "recipes"): Recipe,
    ModelKey("groceries", "recipe_ingredients"): RecipeIngredient,
    ModelKey("tasks", "tasks"): Task,
    ModelKey("habits", "habits"): Habit,
    ModelKey("habits", "habit_completions"): HabitCompletion,
    ModelKey("habits", "leet_code_records"): LeetCodeRecord,
    ModelKey("metrics", "daily_metrics"): DailyMetrics,
    ModelKey("time_tracking", "time_entries"): TimeEntry,
}

def _get_model_class(module: str, subtype: str) -> type[Any] | None:
    return MODEL_CLASSES.get(ModelKey(module, subtype))


@api_bp.route("/<module>/<subtype>/<int:item_id>", methods=["GET", "PATCH", "DELETE"])
@login_plus_session
def item(
    session: Session, module: str, subtype: str, item_id: int
) -> tuple[Response, int]:
    model_class = _get_model_class(module, subtype)
    if model_class is None:
        logger.warning("Unknown model for %s, %s", module, subtype)
        abort(404, description="Requested resource not found")

    item = session.get(model_class, item_id)
    if not item:
        return api_response(
            success=False, message=f"{model_class.__name__} not found."
        ), 404

    # Ownership check
    check_item_ownership(item, current_user.id)

    if request.method == "GET":
        data = item.to_api_dict()

        # Convert weight for display
        if data.get("weight") is not None and current_user.units == UnitSystemEnum.IMPERIAL:
            data["weight"] = kg_to_lbs(data["weight"])
            data["weight_units"] = "lbs"
        elif "weight" in data:
            data["weight_units"] = "kg"

        return api_response(
            success=True, message=f"Retrieved {item.__tablename__}", data=data
        ), 200

    if request.method == "PATCH":
        data = request.get_json()
        for field, value in data.items():
            new_value = value
            if isinstance(value, str):
                with suppress(ValueError):
                    new_value = datetime.fromisoformat(new_value)
            setattr(item, field, new_value)
        session.flush()

        response_data = item.to_api_dict()

        hook = PATCH_HOOKS.get(subtype)
        if hook:
            extra_data = hook(item, data, session, current_user)
            response_data |= extra_data

        return api_response(
            success=True,
            message=f"Successfully updated {model_class.__name__}",
            data=response_data,
        ), 200

    safe_delete(session, item)
    return api_response(
        success=True, message=f"{model_class.__name__} deleted", data=item.to_api_dict()
    ), 200
