# Getting started with exporting to CSV (start with Python's CSV module, MAYBE move to Pandas later when we need data analysis/manipulation before export)

import csv

# employees = [["Name", "Age", "Job"], 
#              ["Spongebob", 30, "Cook"],
#              ["Patrick", 37, "Unemployed"],
#              ["Sandy", 27, "Scientist"]]

with open('filename.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)