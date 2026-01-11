# @property

# Key idea: Python doesn't store the result anywhere, it stores the 'recipe' (the property descriptor)
# on the class, and follows that recipe fresh each time we try to get the value.

# Note when it computes. It's run every single time we access p.age
class Person:
    @property
    def age(self):
        print("Computing age NOW!")
        return 2024 - self.birth_year

p = Person()  # Does NOT compute age
p.birth_year = 1990  # Still NOT computing age
x = p.age  # NOW it computes! (prints "Computing age NOW!")
y = p.age  # Computes AGAIN! (prints again)
# print(x, y)

# so what's the exact sequence?
# 1. "Is 'age' in p.__dict__?"
p.__dict__ # {'birth_year': 1850 } <- no 'age' here

# 2. "Okay, check the class then"
# print(Person.__dict__['age'])   # <- this would show, if printed, something like: <property object at 0x7f03d1063010>

# Step 3: "Oh it's a property (has __get__), not just data"
# So Python does: Person.__dict__['age'].__get__(p, Person)

# Step 4: That __get__ calls your original function with p as self
# Basically: your_age_function(p)