"""
To house collection manipulation functions.
"""
from typing import Any

import logging
logger = logging.getLogger(__name__)

def sort_by_field(items: list[Any], field_name: str, order: str) -> list[Any]:
    """Sort items by field, with nulls last, and respecting asc/desc order."""
    logger.info(f"Sorting by {field_name} ({order})")
    return sorted(
        items,
        key=lambda item: (getattr(item, field_name) is None, getattr(item, field_name)),
        reverse=(order == 'desc')
    )