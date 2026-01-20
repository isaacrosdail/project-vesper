"""
To house collection manipulation functions.
"""

import logging
from typing import TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


def sort_by_field(items: list[T], field_name: str, order: str) -> list[T]:
    """Sort items by field, with `NULL` entries last, and respecting asc/desc order."""
    if not items:
        return items
    logger.info("Sorting %s by %s (%s)", items[0].subtype, field_name, order)
    return sorted(
        items,
        key=lambda item: (getattr(item, field_name) is None, getattr(item, field_name)),
        reverse=(order == "desc"),
    )
