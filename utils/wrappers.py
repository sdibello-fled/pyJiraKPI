import time
from functools import wraps

def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} returned: {result}")
        print(f"Execution time of {func.__name__}: {end - start} seconds")
        return result
    return wrapper