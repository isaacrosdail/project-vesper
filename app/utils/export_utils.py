# Getting started with exporting to CSV (start with Python's CSV module, MAYBE move to Pandas later when we need data analysis/manipulation before export)

# ==================================================================
# TO LEARN:
# Flask Response with the right HTTP headers (Content-Type, Content-Disposition) for downloads
#       Content-Disposition: attachment; filename="whatever.csv"
# MIME type stuff?
# CSV dialects
# Handling special characters, quotes, & commas in data

# DB practice
# efficiently querying data (practice with pagination / chunking for big tables)
# converting DB rows/objects into CSV-friendly formats
# Handling diff data types (dates, booleans, nulls) in exports
# ==================================================================

import csv

# employees = [
#     {"Name": "Spongebob", "Age": 30, "Job": "Cook"},
#     {"Name": "Patrick", "Age": 37, "Job": "Unemployed"},
#     {"Name": "Sandy", "Age": 27, "Job": "Scientist"}
# ]

# with open('filename.csv', 'w') as file:
#     fieldnames = ["Name", "Age", "Job"]
#     writer = csv.DictWriter(file, fieldnames=fieldnames)
#     writer.writeheader()
#     for row in employees:
#         writer.writerow(row)


# Parameters would need to be something like:
# filename for filename
# fieldnames mapping?
# tablename

filename = "filename"    # name user wants for the file -> give this an auto-generated default?
tablename = "employees"  # name of table user wants to export -> have an "all" option?

headers_map = {
    "habits": ["title", "category", "created_at"],
}

habits_data = [
    {"title": "Workout", "category": "Health", "created_at": "Some Datetime"}
]

data_map: dict = {
    "habits": habits_data,
}

def write_table_to_csv(filename: str, tablename: str):

    with open(f"{filename}.csv", 'w', newline='') as file:
        fieldnames = headers_map[tablename]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_map[tablename]:
            writer.writerow(row)

def read_table_csv(filename: str):
    with open(f"{filename}.csv", "r", newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

# with open('filename.csv', 'r') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(row)


def main():

    write_table_to_csv("test1", "habits")
    read_table_csv("test1")

if __name__ == "__main__":
    main()