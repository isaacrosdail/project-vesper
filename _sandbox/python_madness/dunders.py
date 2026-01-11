
# Dunders are essentially behavior contracts.
# Since everything is an object in Python, everything has:
#       1. Attributes ('what') -> properties
#       2. Behavior ('how')    -> dunders

class MyClass:
    def __add__(self, other):  # What happens with +
        return "added!"
    
    def __str__(self):         # What happens with str()
        return "I'm an object!"

obj = MyClass()
obj + 5          # Calls obj.__add__(5)
# print(str(obj))  # Calls obj.__str__()


# dir() shows the object's "interface" - what you can access/call on it:
# It asks "What can I do with this object?"
class Person:
    def __init__(self):
        self.name = "Bob"    # Instance attribute
    
    @property
    def greeting(self):      # Property (descriptor)
        return f"Hi, {self.name}"
    
    def say_hello(self):     # Method
        return "Hello!"

p = Person()
# print(dir(p))  # Shows: name, greeting, say_hello, plus inherited dunders
print(p.__doc__)

# Instance attributes (self.name): p.__dict__
# Methods & properties: Person.__dict__ (the class)
# Built-in behavior: Inherited from parent classes