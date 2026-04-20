from datetime import datetime
from decimal import Decimal
from typing import Any

from flask.json.provider import DefaultJSONProvider
from sqlalchemy import inspect

# Base exclusions applied to all models
EXCLUDE_COLS = ["user_id", "updated_at"]


class APISerializable:
    """
    Mixin that provides automatic JSON serialization for SQLAlchemy models.

    Usage:
        class Task(Base, APISerializable):
            __api_exclude__ = ['due_date'] # Optional: exclude specific fields per-model

            name = Column(String(50))
            ..etc..
    """

    def to_api_dict(self, *, include_relations: bool = False) -> dict[str, Any]:
        """Convert model to JSON-safe dict

        Uses SQLAlchemy introspection to iterate over columns and serialize values.
        Respects exclusion rules from both `EXCLUDE_COLS` constant and model-specific
        `__api_exclude__` attribute.

        Special type handling:
        - datetime: Converted to ISO format string
        - Others: Pass through as-is

        Returns:
            Dict with column names as keys, serialized values, plus 'subtype' field
            from the model's table name for frontend routing.

        Example:
            >>> task = Task(name="My Task", priority=PriorityEnum.HIGH)
            >>> task.to_api_dict()
            {'id': 1, 'name': 'My Task', 'priority': 'HIGH', ...}
        """
        mapper = inspect(self.__class__)

        # Build exclusions from global + model-specific excludes
        exclude = set(EXCLUDE_COLS)
        if hasattr(self, "__api_exclude__"):
            exclude.update(self.__api_exclude__)

        result = {}
        for col in mapper.columns:  # type: ignore[union-attr]
            if col.name in exclude:
                continue
            result[col.name] = getattr(self, col.name)

            # value = getattr(self, col.name)

            # # Adjustments for specific types
            # # if isinstance(value, Enum):
            # #     result[col.name] = value.value
            # if isinstance(value, datetime):
            #     user_tz = ZoneInfo(tz)
            #     result[col.name] = value.astimezone(user_tz).isoformat(timespec='seconds')
            # elif isinstance(value, Decimal):
            #     result[col.name] = round(float(value), 2)
            # else:
            #     result[col.name] = value

        # Include declared properties (from `__api_properties__` lists in each model)
        for prop_name in getattr(self, "__api_properties__", []):
            result[prop_name] = getattr(self, prop_name)

            # value = getattr(self, prop_name)
            # # if isinstance(value, Enum):
            # #     result[prop_name] = value.value
            # if isinstance(value, datetime):
            #     user_tz = ZoneInfo(tz)
            #     result[prop_name] = value.astimezone(user_tz).isoformat(timespec='seconds')
            # elif isinstance(value, Decimal):
            #     result[prop_name] = round(float(value), 2)
            # else:
            #     result[prop_name] = value

        result["subtype"] = self.__tablename__  # type: ignore[attr-defined]

        ## TODO: Trying to truly generalize
        # here, include_relations param must be list[str] = []
        # then pass in something like: item.to_api_dict(include_relations=['ingredients'])
        # if include_relations:
        #     for rel in mapper.relationships:
        #         if rel.key in include_relations:
        #             print(rel.key, file=sys.stderr)

        ## Add ingredients info
        if hasattr(self, "ingredients"):
            result["ingredients"] = [
                {
                    "product_id": ing.product_id,
                    "product_name": ing.product.name,
                    "amount_value": ing.amount_value,
                    "amount_units": ing.amount_units
                }
                for ing in self.ingredients
            ]

        # Tasks web: Add subtasks/supertasks data
        if hasattr(self, "subtasks"):
            result["subtasks"] = [t.id for t in self.subtasks]
            result["supertasks"] = [t.id for t in self.supertasks]

        # Habits, Tasks, & Time Entries: Include pillars (ids)
        # TODO: Clean up
        if hasattr(self, "pillars"):
            result["pillars"] = [
                {"id": p.id, "name": p.name} for p in self.pillars
            ]

        ## TODO: cleanup, for shopping list info
        if hasattr(self, "product"):
            result["net_weight"] = round(float(self.product.net_weight), 2)
            result["unit_type"] = self.product.unit_type

        return result


# jsonify internally calls json.dumps()
# When json.dumps() hits a type it doesn't know (datetime, Decimal), it calls
# a default() method. That's what we're writing here.



class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat(timespec="seconds")
        if isinstance(obj, Decimal):
            return round(float(obj), 2)
        return super().default(obj)

