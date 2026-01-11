# Prob should move to sandbox, but could be useful to learn inspect "in the field" for a bit
import inspect
from typing import Any, Dict, List, Tuple, Type

def get_dunders(obj_or_class: Any) -> Dict[str, Any]:
    """Get all dunder methods/attributes from an object or class.
    
    Args:
        obj_or_class: Instance or class to inspect
        
    Returns:
        Dict mapping dunder names to their values/objects
        
    Example:
        get_dunders(task) -> {'__str__': <method>, '__tablename__': 'tasks', ...}
    """
    # This works, but we can do better.
    # result = {}
    # for name, obj in inspect.getmembers(obj_or_class):
    #     if name.startswith('__') and name.endswith('__'):
    #         result[name] = obj
    # return result
    dunders = {
        k:v for (k,v) in inspect.getmembers(obj_or_class)
        if k.startswith('__') and k.endswith('__')
    }
    return dunders


class MyClass:
    def thing(self) -> str:
        return "hello"

# print(get_dunders(MyClass))



### Let's put the timer decorator stuff here too. Will move this to an appropriate place after:
import time
from functools import wraps


def timer(func): # type: ignore[no-untyped-def]
    """Decorator that prints how long a function takes to run."""
    # Preserves original function's name/docstring
    @wraps(func)   #  <- slow_function gets passed as func
    def wrapper(*args, **kwargs): # type: ignore[no-untyped-def]  # wrapper becomes the new slow_function, so when
        # someone calls slow_function(), theyre actually calling wrapper()
        # YOUR CODE HERE:
        # 1. Record start time
        start = time.time()
        # 2. Call the original function
        result = func(*args, **kwargs)
        # 3. Record end time
        end = time.time()
        print(f"Took {end - start} sec.")
        # 4. Print the difference
        # 5. Return the function's result
        return result
    return wrapper

# Test it:
@timer
def slow_function(): # type: ignore[no-untyped-def]
    time.sleep(1)
    return "done"

print(slow_function())  # Should print timing info + "done"