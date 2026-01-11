# Strategy Pattern
# A type of Behavioral Pattern

# Great when: You have the same OPERATION but different ALGORITHMS for said operation.

# "if you wanna modify or extend the behavior of a class without directly changing it, you can go with the strategy pattern"

# "just always use a strategy pattern"
# fancy talk for "use an interface"?


from abc import ABC, abstractmethod

class FilterStrategy(ABC):

    @abstractmethod
    def removeValue(self, val):
        pass

class RemoveNegativeStrategy(FilterStrategy):

    def removeValue(self, val):
        return val < 0

class RemoveOddStrategy(FilterStrategy):

    def removeValue(self, val):
        return abs(val) % 2


class Values:
    def __init__(self, vals):
        self.vals = vals

    def filter(self, strategy):
        res = []
        for n in self.vals:
            if not strategy.removeValue(n):
                res = res.append(n)
        return res


values = Values([-7, -4, -1, 0, 2, 6, 9])
print(values.filter(RemoveNegativeStrategy()))  # [0, 2, 6, 9]
print(values.filter(RemoveOddStrategy()))         # [-4, 0, 2, 6]


######### The below is from the mention Primeagean makes in the video, relating to one thing he did using the strategy pattern.
# I tried to piece together and use an LLM to fill in some blanks so we can properly study something concrete.
# Here's the result of that:

# The Netflix scenario: They're processing streaming metrics in real-time. Sometimes you want:
# Continuous aggregation: "Total bytes sent since stream started" (always includes previous values)
# Windowed aggregation: "Bytes sent in last 10 seconds" (only current window, resets)
# Both need the same interface but totally different behaviors. Classic Strategy pattern territory.

# Here's what his "emitters" probably looked like:
class DataEmitter(ABC):
    @abstractmethod
    def emit(self, new_value, timestamp):
        pass

class ContinuousEmitter(DataEmitter):
    def __init__(self):
        self.total = 0
    
    def emit(self, value, timestamp):
        self.total += value
        return self.total  # Always includes history

class WindowedEmitter(DataEmitter):
    def __init__(self, window_seconds=10):
        self.window = []
        self.window_size = window_seconds
    
    def emit(self, value, timestamp):
        # Remove old values, add new, return sum
        self.window = [(v, t) for v, t in self.window if t > timestamp - self.window_size]
        self.window.append((value, timestamp))
        return sum(v for v, _ in self.window)