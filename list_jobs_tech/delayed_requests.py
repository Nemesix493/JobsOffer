import requests
import time
import random
from functools import wraps

TEMPO_MIN = 4
TEMPO_MEAN = 10

def temporise(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        time.sleep(
            TEMPO_MIN + random.randrange(
                0,
                (TEMPO_MEAN - TEMPO_MIN) * 2 * 1000
            ) / 1000.0
        )
        return func(*args, **kwargs)
    return wrapped

tempo_requests_get = temporise(requests.get)