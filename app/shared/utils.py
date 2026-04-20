# Interim catch-all file for helpers which don't quite justify their own files

import logging
from collections import defaultdict, deque
from datetime import date
from typing import Any, Literal, TypeVar

from flask import request, session

T = TypeVar("T")

logger = logging.getLogger(__name__)




def set_toast(message: str, toast_type: str = "info") -> None:
    """
    Queues a toast for display after redirect.
    JS reads from `data-toast` on body (base.html) and displays it.

    Options for toast_type: `error`, `success`, `info`, `warning` (default: `info`)
    """
    session["toast"] = {"message": message, "type": toast_type}


def sort_by_field(items: list[T], field_name: str, order: str) -> list[T]:
    """Sort items by field, with `NULL` entries last, and respecting asc/desc order."""
    if not items:
        return items

    logger.info(
        "Sorting %s by %s (%s)",
        type(items[0]).__name__,
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


def is_acyclic(links: list[tuple[int, int]]) -> bool:
    """Kahn's algorithm to perform topological sort & check acyclicity of task dependencies."""
    task_ids = {n for edge in links for n in edge}
    in_degree = dict.fromkeys(task_ids, 0)
    adj_map = defaultdict(list)

    for child, parent in links:
        in_degree[child] += 1
        adj_map[parent].append(child)

    queue = deque(tid for tid, deg in in_degree.items() if deg == 0)
    processed = 0

    while queue:
        node_id = queue.popleft()
        processed += 1
        for entry in adj_map.get(node_id, []):
            in_degree[entry] -= 1
            if in_degree[entry] == 0:
                queue.append(entry)

    return processed == len(task_ids)


def calculate_bmr(sex: Literal["m", "f"], weight_kg: float, height_cm: float, birth_year: int) -> float:
    """
    Mifflin-St Jeor equation for resting BMR calculation.

    Females: (10 * weight[kg]) + (6.25 * height[cm]) - (5 * age[yrs]) - 161

    Males:   (10 * weight[kg]) + (6.25 * height[cm]) - (5 * age[yrs]) + 5
    """
    age = date.today().year - birth_year
    constant = -161 if sex == "f" else 5
    return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + constant
