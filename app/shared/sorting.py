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

from typing import Any, List

# Stable
def bubble_sort_simple(myList: list[Any]) -> None:
    # Outer loop decides whether to continue
    for i in range(len(myList)-1):
        no_swaps = True
        for j in range(len(myList)-i-1):
            # If arr[j] > arr[j+1], swap
            if myList[j] > myList[j+1]:
                no_swaps = False
                temp = myList[j]
                myList[j] = myList[j+1]
                myList[j+1] = temp
        if no_swaps:
            break

# Stable
def bubble_sort(myList: List[Any], key: str, reverse: bool = False) -> None:
    """
    Sort a list of object in place using bubble sort algorithm.
    Args:
        myList: List of objects to sort
        key: Name of the attribute by which to sort (as string)
        reverse: If True, sort in descending order. If False, ascending. Default: False
    Returns:
        None (modifies the list in place)
    """
    # Outer loop decides whether to continue
    for i in range(len(myList)-1):
        no_swaps = True
        for j in range(len(myList)-i-1):
            # Choose which comparison to use
            if reverse:
                # Swap current with next if it's less than (smaller bubbles up to end of list)
                should_swap = getattr(myList[j], key) < getattr(myList[j+1], key)
            else:
                # Swap current with next it it's greater than (largest bubbles up to end of list)
                should_swap = getattr(myList[j], key) > getattr(myList[j+1], key)
            if should_swap:
                no_swaps = False
                temp = myList[j]
                myList[j] = myList[j+1]
                myList[j+1] = temp
        # If we traverse the entire array once without swapping, we have fully sorted the list
        if no_swaps:
            break
