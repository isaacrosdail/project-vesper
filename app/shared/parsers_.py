"""
Parses raw HTTP form and request data into cleaned dictionaries.

Normalizes incoming values:
- Strings -> stripped strings ("" if missing)
- Enums   -> uppercased, except unit_type & UserLang (lowercase by convention)
- Numbers/dates -> parsed values or None
- Checkboxes -> booleans

Includes small helpers for parsing request args used by API routes.
"""

from collections.abc import Callable
from typing import Any

from flask import request

from app.shared.decorators import log_parser


def _stripped(val: str | None) -> str | None:
    """Strip whitespace, return None if empty."""
    if val is None:
        return None
    stripped = val.strip()
    return stripped or None

def _upper_or_none(val: str | None) -> str | None:
    """Upper, NO stripping. For enums, so we want to catch bad frontend data."""
    return val.upper() if val else None

def _passthrough(val: str | None) -> str | None:
    """Leave intact, empty values resolve to None."""
    return val or None

def parse_checkbox(val: str | None) -> bool:
    """Resolve HTML checkbox states (on, None) to (True, False)"""
    return val is not None


@log_parser
def parse_form(form_data: dict[str, str], schema: dict[str, Callable[[str | None], Any]]) -> dict[Any, Any]:
    results = {}
    for entry, parser_func in schema.items():
        entry_val = form_data.get(entry)
        results[entry] = parser_func(entry_val)
    return results


# AUTH
USER_SCHEMA = {
    "username": _stripped,
    "password": _stripped,
    "name": _stripped,
}

# GROCERIES
PRODUCT_SCHEMA = {
    "barcode": _stripped,
    "name": _stripped,
    "net_weight": _stripped,
    "category": _upper_or_none,
    "unit_type": _upper_or_none,
    "calories_per_100g": _stripped,
}

TRANSACTION_SCHEMA = {
    "price_at_scan": _stripped,
    "quantity": _stripped,
}

# HABITS
HABIT_SCHEMA = {
    "name": _stripped,
    "target_frequency": _stripped,
    "is_promotable": parse_checkbox,
}

LEETCODE_SCHEMA = {
    "leetcode_id": _stripped,
    "title": _stripped,
    "difficulty": _upper_or_none,
    "language": _upper_or_none,
    "status": _upper_or_none,
}

# METRICS
DAILY_METRICS_SCHEMA = {
    "entry_date": _passthrough,
    "steps": _stripped,
    "weight": _stripped,
    "weight_units": _passthrough,
    "calories": _stripped,
    "wake_datetime": _passthrough,
    "sleep_datetime": _passthrough,
}

# TASKS
TASK_SCHEMA = {
    "name": _stripped,
    "priority": _upper_or_none,
    "due_date": _passthrough,
    "is_frog": parse_checkbox,
}

# TIME_TRACKING
TIME_ENTRY_SCHEMA = {
    "category": _stripped,
    "description": _stripped,
    "entry_date": _passthrough,
    "started_at": _passthrough,
    "ended_at": _passthrough,
}

def get_table_params(prefix: str, default_sort: str) -> dict[str, Any]:
    """
    Extracts table state parameters from request query parameters and
    returns them as a dict.

    Args:
        subtype: The table/entity type (eg., 'habits', 'time_entries')
        default_sort: The default field to sort by if not specified in query params

    Returns:
        Dict with 'range' (days to query), 'sort_by' (field to be used as key),
        and 'order' (asc/desc)
    """
    return {
        "range": request.args.get(f"{prefix}_range", 7, type=int),
        "sort_by": request.args.get(f"{prefix}_sort", default_sort),
        "order": request.args.get(f"{prefix}_order", "desc"),
    }
