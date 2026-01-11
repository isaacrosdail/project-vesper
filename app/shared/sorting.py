"""
Sorting algorithms library.

Implements classic sorting algorithms for practice.
Each algorithm:
- Operates in place unless otherwise noted.
- Is annotated with stability characteristics.
- Will be evaluated for time and space complexity.

NOTE:
These implementations are obviously for learning purposes only.
I would of course use Python's built-in `sorted()` or database `ORDER BY` in
any real-world scenario.
"""

from typing import Any


# Stable
def bubble_sort_simple(my_list: list[Any]) -> None:
    # Outer loop decides whether to continue
    for i in range(len(my_list)-1):
        no_swaps = True
        for j in range(len(my_list)-i-1):
            # If arr[j] > arr[j+1], swap
            if my_list[j] > my_list[j+1]:
                no_swaps = False
                temp = my_list[j]
                my_list[j] = my_list[j+1]
                my_list[j+1] = temp
        if no_swaps:
            break

# Stable
def bubble_sort(my_list: list[Any], key: str, *, reverse: bool = False) -> None:
    """
    Sort a list of object in place using bubble sort algorithm.
    Args:
        my_list: List of objects to sort
        key: Name of the attribute by which to sort (as string)
        reverse: If True, sort in descending order. If False, ascending. Default: False
    Returns:
        None (modifies the list in place)
    """
    # Outer loop decides whether to continue
    for i in range(len(my_list)-1):
        no_swaps = True
        for j in range(len(my_list)-i-1):
            if reverse:
                # Swap current with next if it's less than (smaller bubbles to end)
                should_swap = getattr(my_list[j], key) < getattr(my_list[j+1], key)
            else:
                # Swap current with next it it's greater than (largest bubbles to end)
                should_swap = getattr(my_list[j], key) > getattr(my_list[j+1], key)
            if should_swap:
                no_swaps = False
                temp = my_list[j]
                my_list[j] = my_list[j+1]
                my_list[j+1] = temp
        # traverse 1x without swap => sorted fully
        if no_swaps:
            break
