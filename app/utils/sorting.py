# Will be implementing my own versions of the major sorting algorithms here for learning/practice
# and invoking them across Vesper
# Later: Study time & space complexities of each
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
def bubble_sort(myList):
    # Outer loop decides whether to continue
    for i in range(len(myList)-1):
        no_swaps = True
        for j in range(len(myList)-i-1):
            # If arr[i] > arr[i+1], swap
            if myList[j] > myList[j+1]:
                no_swaps = False
                temp = myList[j]
                myList[j] = myList[j+1]
                myList[j+1] = temp
        if no_swaps == True:
            break

# Stable
def bubble_sort_test(myList, key, reverse=False):
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
        if no_swaps == True:
            break

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

#
def bucket_sort():
    pass

def bogo_sort():
    pass

# Timsort - Hybrid, stable
def timsort():
    pass


'''
# Main function for testing these for now
def main():

    # List of dicts
    test_data = [
        {"title": "Try me", "priority": 3},
        {"title": "Test me", "priority": 1},
        {"title": "Another task", "priority": 2}
    ]
    #print(test_data)

    # Test objects
    task1 = SimpleTask("Try me", 3)
    task2 = SimpleTask("Test me", 1)
    task3 = SimpleTask("Another task", 2)
    test_objects = [task1, task2, task3]
    print(test_objects)
    bubble_sort_test(test_objects, "title")
    print(test_objects)

    myList = [7, 4, 2, 1, 0]
    print(myList)

    bubble_sort(myList)
    print(myList)


if __name__ == "__main__":
    main()
    '''