# Iterator Pattern: defines how the values in an object can be iterated through
# Also a Behavioral Pattern

# __iter__() returns self, __next__() advances + raises StopIteration (to say it's done?)
# OR use yield for automatic state management
# Protocol vs generator convenience trade-off (same as JS)

class Range:
    def __init__(self, end): self.end, self.current = end, 0
    def __iter__(self): return self
    def __next__(self):
        if self.current < self.end:
            self.current += 1; return self.current - 1
        raise StopIteration

class ListNode:
    def __init__(self, val):
        self.val = val
        self.next = None

# Open-Closed principle for classes: Basically self-evident but applies at the class boundary and
# says "LinkedList should be open to new behaviors via methods or subclassing, but closed to modification of its internal traversal logic."
# Example code gotten from YT video: https://www.youtube.com/watch?v=ZfG8BSTX0Lw&t=1031s
class LinkedList:
    def __init__(self, head):
        self.head = head
        self.curr = None

    # Define Iterator
    def __iter__(self):
        self.cur = self.head
        return self

    # Iterate
    def __next__(self):
        if self.cur:
            val = self.cur.val
            self.cur = self.cur.next
            return val
        else:
            raise StopIteration    # other langs use "options"? tf is that?

# Initialize LinkedList
head = ListNode(1)
head.next = ListNode(1)
head.next.next = ListNode(1)
my_list = LinkedList(head)

# Iterate thru LinkedList
for n in my_list:
    print(n)