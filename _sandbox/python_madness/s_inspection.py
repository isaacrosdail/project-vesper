import inspect


# The beautiful consistency:

# dir() = "What can I access?"
# vars() = "What's stored on this instance?"
# help() = "How do I use this?"
# type() = "What kind of object is this?"
# inspect module = "Tell me EVERYTHING"

# Shows docstring, sig, usage examples
# It's reading obj.__doc__ plus analyzing the signature
# help(str.upper)

# vars(obj) is just obj.__dict__ in disguise
class Person:
    def __init__(self): self.name = "Bob"

p = Person()
# vars(p)        # {'name': 'Bob'}
# p.__dict__      # {'name': 'Bob'} - same thing!

# We can even get source code of..our code?
# print(inspect.getsource(p.__class__))

# and this returns the filepath where the function is defined
# print(inspect.getsourcefile(p.__class__))

# print(type(p))


# Properties are computed attributes, and are stored as descriptor objects on class dictionary
# Dynamically computed when accessed
class Person:
    @property
    def greeting(self):
        return "Hello"

# The property descriptor is stored on the CLASS
Person.__dict__['greeting']  # <property object at 0x...>

# NOT stored on instances
p = Person()
print(vars(p))  # {} - empty! No 'greeting' here, since vars only shows STORED attributes
print(getattr(p, 'greeting'))
# ... The magic happens during attr access
# print(p.greeting)  # What actually happens:

# 1. Python checks p.__dict__ for 'greeting' - not found
# 2. Python checks Person.__dict__ for 'greeting' - found a property descriptor
# 3. Since it's a descriptor, Python calls property.__get__(p, Person)
# 4. That calls your original function with p as 'self'
# 5. Returns "Hello"