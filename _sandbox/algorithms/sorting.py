"""
Sorting algorithms library (practice/expansion stuff here).
Each algorithm:
- Operates in place unless otherwise noted.
- Is annotated with stability characteristics.
- Will be evaluated for time and space complexity.

- (TODO) selection_sort, insertion_sort, quick_sort, merge_sort, etc.
"""

from typing import Any, List

'''
So say we have myList = [1, 6, 3, 9, 0]
1. 1 vs 6 -> no swap
2. 6 vs 3 -> swap ---> so now? myList = [1, 3, 6, 9, 0]
3. 6 vs 9 -> no swap
4. 9 vs 0 -> swap
So after one pass:
    myList = [1, 3, 6, 0, 9]

could we raise efficiency by saving the value for the lowest somehow?
After first pass: = [1, 3, 9, 0, 6]
'''

# Class to make Task objects for testing
class SimpleTask:
    def __init__(self, title, priority):
        self.title = title
        self.priority = priority

# Stable
def bubble_sort_simple(myList):
    """Already implemented."""

# Stable
def bubble_sort(myList: List[Any], key: str, reverse: bool = False) -> None:
    """Already implemented."""

# Slightly more efficient than bubble sort
def selection_sort():
    pass

# Good for small datasets
# Stable
def insertion_sort():
    pass

# Faster, but more complex
# Divide & conquer, choose a pivot and partition the array around that.
# Generally not stable
def quick_sort():
    pass

# Most implementations produce a stable sort
def merge_sort():
    pass

# Stable
def count_sort():
    pass

def bucket_sort():
    pass

def bogo_sort():
    pass

# Timsort - Hybrid, stable
def timsort():
    pass