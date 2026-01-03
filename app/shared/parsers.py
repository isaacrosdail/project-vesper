"""
Parses raw HTTP form and request data into cleaned dictionaries.

Normalizes incoming values:
- Strings -> stripped strings ("" if missing)
- Enums   -> uppercased, except unit_type & UserLang (lowercase by convention)
- Numbers/dates -> parsed values or None
- Checkboxes -> booleans

Includes small helpers for parsing request args used by API routes.
"""
from typing import Any

from flask import request

from app.shared.decorators import log_parser


def _upper_or_none(val: str | None) -> str | None:
    return val.upper() if val else None

def parse_barcode(val: str) -> str | None:
    """Parse barcode. Strip whitespace, return None if empty."""
    return val.strip() if val else None

def parse_checkbox(val: str | None) -> bool:
    """Resolve HTML checkbox states (on, None) to (True, False)"""
    return val is not None

@log_parser
def parse_product_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "barcode": (form_data.get("barcode") or "").strip(),
        "name": (form_data.get("name") or "").strip(),
        "net_weight": form_data.get("net_weight", "").strip(),
        "category": _upper_or_none(form_data.get("category")),
        "unit_type": _upper_or_none(form_data.get("unit_type")),
        "calories_per_100g": form_data.get("calories_per_100g", "").strip(),
    }

@log_parser
def parse_transaction_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "price_at_scan": form_data.get("price_at_scan", "").strip(),
        "quantity": form_data.get("quantity", "").strip()
    }

@log_parser
def parse_user_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "username": (form_data.get("username") or "").strip(),
        "password": (form_data.get("password") or ""),
        "name": (form_data.get("name") or "").strip(),
    }

@log_parser
def parse_task_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": (form_data.get("name") or "").strip(),
        "priority": _upper_or_none(form_data.get("priority")),
        "due_date": form_data.get("due_date") or None,
        "is_frog": parse_checkbox(form_data.get("is_frog"))
    }

@log_parser
def parse_leetcode_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "leetcode_id": form_data.get("leetcode_id", "").strip(),
        "title": (form_data.get("title") or "").strip(),
        "difficulty": _upper_or_none(form_data.get("difficulty")),
        "language": _upper_or_none(form_data.get("language")),
        "status": _upper_or_none(form_data.get("lcstatus"))
    }

@log_parser
def parse_time_entry_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "category": (form_data.get("category") or "").strip(),
        "description": (form_data.get("description") or "").strip(),
        "entry_date": form_data.get("entry_date") or None,
        "started_at": form_data.get("started_at") or None,
        "ended_at": form_data.get("ended_at") or None,
    }

@log_parser
def parse_habit_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": (form_data.get("name") or "").strip(),
        "target_frequency": (form_data.get("target_frequency") or "").strip(),
        "is_promotable": parse_checkbox(form_data.get("is_promotable")),
    }

@log_parser
def parse_daily_entry_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_date": form_data.get("entry_datetime") or None,
        "steps": (form_data.get("steps") or "").strip(),
        "weight": (form_data.get("weight") or "").strip(),
        "calories": (form_data.get("calories") or "").strip(),
        "wake_time": (form_data.get("wake_time") or "").strip(),
        "sleep_time": (form_data.get("sleep_time") or "").strip(),
    }


def get_table_params(prefix: str, default_sort: str) -> dict[str, Any]:
    """
    Extracts table state parameters from request query parameters and returns them as a dict.

    Args:
        subtype: The table/entity type (eg., 'habits', 'time_entries')
        default_sort: The default field to sort by if not specified in query params

    Returns:
        Dict with 'range' (days to query), 'sort_by' (field to be used as key), and 'order' (asc/desc)
    """
    return {
        'range': request.args.get(f"{prefix}_range", 7, type=int),
        'sort_by': request.args.get(f"{prefix}_sort", default_sort),
        'order': request.args.get(f"{prefix}_order", "desc")
    }