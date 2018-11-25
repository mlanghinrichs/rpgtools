import time
from functools import wraps

def time_me(func):
    """Wrap a function to time its execution and print to console."""
    @wraps(func)
    def dec(*args, **kwargs):
        # Initiate stopwatch (ms)
        curr = int(round(time.time() * 1000))
        # Execute func()
        r = func(*args, **kwargs)
        # Clock out (ms)
        print("Time elapsed: %d" % (int(round(time.time() * 1000)) - curr))
        # Return whatever value func() produced
        return r
    return dec
