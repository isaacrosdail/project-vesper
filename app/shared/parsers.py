"""
Parses form_data into new, cleaned dictionaries.

Normalize raw HTTP form inputs into clean dicts.

- Strings -> (value or "").strip()
- Enums   -> .upper(), except unit_type & UserLang (lowercase by standard)
- Numbers/dates -> value or None
- Checkboxes -> .get(..) is not None (to normalize to bools)
"""
from typing import Any

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

@log_parser
def parse_abtest_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": (form_data.get("title") or "").strip(),
        "hypothesis": (form_data.get("hypothesis") or "").strip(),
        "variant_a_label": (form_data.get("variant_a_label") or "").strip(),
        "variant_b_label": (form_data.get("variant_b_label")or "").strip(),
        "success_condition": (form_data.get("success_condition")or "").strip()
    }

@log_parser
def parse_abtrial_form_data(form_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "abtest_id": (form_data.get("abtest_id") or "").strip(),
        "variant": form_data.get("variant"),
        "is_success": parse_checkbox(form_data.get("is_success")),
        "notes": (form_data.get("notes") or "").strip()
    }