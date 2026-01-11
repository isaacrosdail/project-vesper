from datetime import datetime
from collections import defaultdict

class Transaction:
    def __init__(self, amount, date, category):
        self.amount = amount
        self.date = date
        self.category = category

list = [
    Transaction(10.00, datetime(2025, 10, 21), "Fun"),
    Transaction(9.99, datetime(2025, 10, 21), "Clothes"),
    Transaction(3.41, datetime(2025, 10, 24), "Entertainment"),
    Transaction(2.35, datetime(2025, 10, 12), "Fun")
]

# This lets our loop below sum per category nicely
sums = defaultdict(float)

for item in list:
    sums[item.category] += item.amount

print(sums)