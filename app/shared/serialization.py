
from typing import Any

from sqlalchemy import inspect

from enum import Enum
from datetime import datetime

# Base exclusions applied to all models
EXCLUDE_COLS = ['user_id', 'updated_at']


class APISerializable:
    """
    Mixin that provides automatic JSON serialization for SQLAlchemy models.

    Usage:
        class Task(Base, APISerializable):
            __api_exclude__ = ['due_date'] # Optional: exclude specific fields per-model

            name = Column(String(50))
            ..etc..
    
    Behavior:
        - Handles type conversions: Enum -> str, datetime -> ISO 8601
        - Excludes fields in EXCLUDE_COLS by default (user_id, updated_at)
    
    Example:
        >>> task = Task(name="My Task", priority=PriorityEnum.HIGH)
        >>> task.to_api_dict()
        {'id': 1, 'name': 'My Task', 'priority': 'HIGH', ...}
    """

    def to_api_dict(self) -> dict[str, Any]:
        """Convert model to JSON-safe dict"""

        # Mapper is a Mapper object - SQLAlchemy's internal representation of how our Python class Task maps to a DB table
        mapper = inspect(self.__class__) # self is our Task instance
        # mapper.columns is a collection of Column objects (not the values, the column definitions themselves)

        # Configuring excludes based on both base exclude list here + whatever the model itself dictates
        exclude = set(EXCLUDE_COLS)

        # Check if THIS model added more exclusions
        if hasattr(self, '__api_exclude__'):
            exclude.update(self.__api_exclude__)

        result = {}
        # 'col' here is the Column definition (the blueprint)
        # Its type is a Column object from SQLAlchemy
        for col in mapper.columns: # type: ignore
            # 'col.name' would be the name of the field/column, like 'priority', 'due_date', etc
            # print(f"Column {col.name}, Value: {getattr(self, col.name)}", file=sys.stderr)

            if col.name in exclude:
                continue # skip excluded fields

            # 'value' here is the actual data in this instance
            # Represents the actual values stored in this Task instance (ie, 'PriorityEnum.LOW', 'datetime(2025, 10, 7)', '7', etc)
            # Its type is whatever Python type the data is
            value = getattr(self, col.name)

            if isinstance(value, Enum):
                result[col.name] = value.value
            elif isinstance(value, datetime):
                result[col.name] = value.isoformat()
            else:
                result[col.name] = value

        # print(result, file=sys.stderr)

        # Append subtype to each as well, for frontend's sake
        result["subtype"] = self.__tablename__ # type: ignore
        return result