
############ TEST / PRACTICE 1
# When announce(hello) runs:
# If defines the wrapper function, returns the wrapper object, then
# that returned wrapper gets assigned to wrapped_hello()
# def announce(fn):
#     def wrapper():
#         print("Before the function runs")
#         fn()
#         print("After the function runs")
#     return wrapper

# def hello():
#     print("Hello!")

# # Manual wrapping, no @
# # So at read time, we're loading the gun (wrapped_hello()) with the bullet (announce(hello))
# wrapped_hello = announce(hello)

# print("Calling original hello():")
# hello()

# print("\nCalling wrapped_hello():")
# # At call time, we pull the trigger - the wrapper fires, printing "before", running hello(), then printing "after"
# wrapped_hello()
##############


############## TEST / PRACTICE 2
# def announce(fn):
#     print("announce() called — wrapping", fn.__name__)
#     def wrapper():
#         print(f"Before {fn.__name__}")
#         fn()
#         print(f"After {fn.__name__}")
#     return wrapper

# def greet():
#     print("Hello!")

# print(">>> Assigning wrapped_greet")
# wrapped_greet = announce(greet)  # read-time wrapping

# print(">>> Calling wrapped_greet")
# wrapped_greet()

# print(">>> Calling announce(greet)() directly")
# announce(greet)()

### Step by Step:
# 1. Python defines announce (no output yet)
# 2. Python defines greet (no output yet)
# 3. Prints: >>> Assigning wrapped_greet
# 4. Executes wrapped_greet = announce(greet)
#       - Calls announce immediately with fn = greet
#       - Inside announce, prints: announce() called - wrapping greet
#       - Builds a new wrapper function (closing over greet)
#       - Returns that wrapper; wrapped_greet now points to it
#           No "before"/"after" yet - the wrapper hasn't been called
# 5. Prints: >>> Calling wrapped_greet
# 6. Executes wrapped_greet
#       - This calls the wrapper created in step 4
#       - Wrapper prints: Before greet
#       - 
# 
# 

# # 1. Defines our function
# def say_hi():
#     print("Hi")

# # 2. Defines the wrapper factory
# # When we call wrapped_hi(say_hi), Python:
# def wrapped_hi(fn):         # <- Passes the function object say_hi into fn
#     print("wrapping...")    # <- Prints "wrapping..." (because that line is at the top level of wrapped_hi)
#     def wrapped_func():     # <- Defines wrapped_func (a closure over fn)
#         print("Before")
#         fn()
#         print("After")
#     return wrapped_func     # <- Returns the wrapped_func object
# # NOTE: It does not run wrapped_func yet - it just returns it.

# wrapped_hi(say_hi)      # <- Doing only this just prints "wrapping..."
# # That's cause we're only calling wrapped_hi, but are ignoring what it returns

# # We need to store the function in a variable and then call it, like:
# new_hi = wrapped_hi(say_hi)
# new_hi()

##############


############## TEST / PRACTICE 3
def log_call(fn):
    def wrapper(*args, **kwargs):
        print(f"Calling {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"Finished {fn.__name__}")
        return result
    return wrapper

@log_call
def greet(name):
    print(f"Hi {name}")

greet("Alice")
greet("John")