from datetime import datetime
from enum import Enum
from typing import Any

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

    def to_api_dict(self) -> dict[str, Any]:
        """Convert model to JSON-safe dict

        Uses SQLAlchemy introspection to iterate over columns and serialize values.
        Respects exclusion rules from both `EXCLUDE_COLS` constant and model-specific
        `__api_exclude__` attribute.

        Special type handling:
        - Enum: Converted to .value
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

            value = getattr(self, col.name)

            # Adjustments for specific types
            if isinstance(value, Enum):
                result[col.name] = value.value
            elif isinstance(value, datetime):
                result[col.name] = value.isoformat()
            else:
                result[col.name] = value

        result["subtype"] = self.__tablename__  # type: ignore[attr-defined]
        return result
