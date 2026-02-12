# Prob should move to sandbox, but could be useful to learn inspect "in the field" for a bit
import inspect
from typing import Any


def get_dunders(obj_or_class: Any) -> dict[str, Any]:
    """Get all dunder methods/attributes from an object or class.

    Args:
        obj_or_class: Instance or class to inspect

    Returns:
        Dict mapping dunder names to their values/objects

    Example:
        get_dunders(task) -> {'__str__': <method>, '__tablename__': 'tasks', ...}
    """
    return {
        k: v
        for (k, v) in inspect.getmembers(obj_or_class)
        if k.startswith("__") and k.endswith("__")
    }
