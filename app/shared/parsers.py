"""
Parses form_data into new, cleaned dictionaries.

Normalize raw HTTP form inputs into clean dicts.

- Strings -> (value or "").strip()
- Enums   -> .upper(), except unit_type & UserLang (lowercase by standard)
- Numbers/dates -> value or None
- Checkboxes -> .get(..) is not None (to normalize to bools)
"""


def _upper_or_none(val: str | None) -> str | None:
    return val.upper() if val else None

def parse_barcode(val: str) -> dict:
    """Parse barcode. Strip whitespace, return None if empty."""
    return val.strip() if val else None

def parse_checkbox(val: str | None) -> bool:
    """Resolve HTML checkbox states (on, None) to (True, False)"""
    return val is not None


def parse_product_data(form_data: dict) -> dict:
    return {
        "barcode": (form_data.get("barcode") or "").strip(),
        "name": (form_data.get("name") or "").strip(),
        "net_weight": form_data.get("net_weight", "").strip(),
        "category": _upper_or_none(form_data.get("category")),
        "unit_type": _upper_or_none(form_data.get("unit_type")),
        "calories_per_100g": form_data.get("calories_per_100g", "").strip(),
    }

def parse_transaction_data(form_data: dict) -> dict:
    return {
        "price_at_scan": form_data.get("price_at_scan", "").strip(),
        "quantity": form_data.get("quantity", "").strip()
    }

def parse_user_form_data(form_data: dict) -> dict:
    return {
        "username": (form_data.get("username") or "").strip(),
        "password": (form_data.get("password") or ""),
        "name": (form_data.get("name") or "").strip(),
    }

def parse_task_form_data(form_data: dict) -> dict:
    return {
        "name": (form_data.get("name") or "").strip(),
        "priority": _upper_or_none(form_data.get("priority")),
        "due_date": form_data.get("due_date") or None,
        "is_frog": parse_checkbox(form_data.get("is_frog"))
    }

def parse_leetcode_form_data(form_data: dict) -> dict:
    return {
        "leetcode_id": form_data.get("leetcode_id", "").strip(),
        "title": (form_data.get("title") or "").strip(),
        "difficulty": _upper_or_none(form_data.get("difficulty")),
        "language": _upper_or_none(form_data.get("language")),
        "status": _upper_or_none(form_data.get("lcstatus"))
    }

def parse_time_entry_form_data(form_data: dict) -> dict:
    return {
        "category": (form_data.get("category") or "").strip(),
        "description": (form_data.get("description") or "").strip(),
        "entry_date": form_data.get("entry_date") or None,
        "started_at": form_data.get("started_at") or None,
        "ended_at": form_data.get("ended_at") or None,
        "duration_minutes": form_data.get("duration_minutes") or None
    }

def parse_habit_form_data(form_data: dict) -> dict:
    return {
        "name": (form_data.get("name") or "").strip(),
        "is_promotable": parse_checkbox(form_data.get("is_promotable")),
    }

def parse_daily_entry_form_data(form_data: dict) -> dict:
    return {
        "steps": (form_data.get("steps") or "").strip(),
        "weight": (form_data.get("weight") or "").strip(),
        "calories": (form_data.get("calories") or "").strip(),
        "wake_time": (form_data.get("wake_time" or "")).strip(),
        "sleep_time": (form_data.get("sleep_time" or "")).strip(),
    }