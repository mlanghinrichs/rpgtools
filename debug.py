import time
from functools import wraps

# Timer wrapper for debugging hefty probability functions
def time_me(f):
    @wraps(f)
    def dec(*args, **kwargs):
        # Initiate stopwatch (ms)
        curr = int(round(time.time() * 1000))

        r = f(*args, **kwargs)

        # Clock out (ms)
        print("Time elapsed: %d" % (int(round(time.time() * 1000)) - curr))
        return r
    return dec