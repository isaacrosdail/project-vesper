
# Iterable: An object/collection that can return its elements once at a time
# An iterable is any object that implements __iter__() (which returns an iterator) OR __getitem__() with sequential indices starting at 0.
# Examples: lists, dicts, sets, strings, generator objects, etc.

# 1. Use iter() and next() to grab only the first key-value pair and print it.
# Expected Output: ('name', 'Isaac')
data1 = {"name": "Isaac", "age": "25", "city": "Vermillion"}

# # Loops through key-value pairs as tuples
# for item in data.items():
#     print(item)

# # Loops through keys only
# for item in data:
#     print(item)

# 1. Print each key and its value on separate lines
data2 = {"steps": "8000", "weight": "175", "mood": "good"}
# Expected output:
# steps
# 8000
# weight
# 175
# mood
# good

# Solution:
# for key, value in data.items():
#     print(key)
#     print(value)

# 2. Same thing, but only print items where the value is NOT empty
# Note: empty strings in Python are falsy
data3 = {"steps": "8000", "weight": "", "mood": "good", "calories": ""}
# Expected output:
# steps
# 8000
# mood
# good

# Solution:
# for key, value in data.items():
#     if value:
#         print(key)
#         print(value)

# 3. Same filtering, but also count how many valid items you processed.
data = {"steps": "8000", "weight": "", "mood": "good", "calories": "", "sleep": "7"}
# Expected output:
# steps
# 8000
# mood
# good
# sleep
# 7
# Processed 3 items

count = 0
for key, value in data.items():
    if value:
        count += 1
        print(key)
        print(value)
print(f"Processed {count} items")