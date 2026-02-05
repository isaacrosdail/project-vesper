# Interim catch-all file for helpers which don't quite justify their own files

import logging
from typing import TypeVar, Any, Protocol

from flask import request

class HasSubtype(Protocol):
    subtype: str

T = TypeVar("T", bound=HasSubtype)

logger = logging.getLogger(__name__)


def sort_by_field(items: list[T], field_name: str, order: str) -> list[T]:
    """Sort items by field, with `NULL` entries last, and respecting asc/desc order."""
    if not items:
        return items

    logger.info(
        "Sorting %s by %s (%s)",
        items[0].subtype,
        field_name,
        order
    )

    return sorted(
        items,
        key=lambda item: (getattr(item, field_name) is None, getattr(item, field_name)),
        reverse=(order == "desc"),
    )

# CONVERSIONS
def kg_to_lbs(value: float) -> float:
    return float(value) * 2.204623

def lbs_to_kg(value: float) -> float:
    return value / 2.204623



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