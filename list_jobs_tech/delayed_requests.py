import requests
from time import sleep
from random import randrange
from functools import wraps


class DelayedRequest:
    def __init__(self, delay_min: int = 1, delay_mean: int = 2):
        self._delay_min = delay_min
        self._delay_mean = delay_mean

    @property
    def delay_mean(self) -> int:
        return self._delay_mean

    @property
    def delay_min(self) -> int:
        return self._delay_min

    @property
    def delay(self):
        return self.delay_min + randrange(
            0,
            (self.delay_mean - self.delay_min) * 2 * 1000
        ) / 1000.0

    @wraps(requests.get)
    def get(self, *args, **kwargs):
        sleep(self.delay)
        return requests.get(*args, **kwargs)

    @wraps(requests.post)
    def post(self, *args, **kwargs):
        sleep(self.delay)
        return requests.post(*args, **kwargs)

    @wraps(requests.put)
    def put(self, *args, **kwargs):
        sleep(self.delay)
        return requests.put(*args, **kwargs)

    @wraps(requests.patch)
    def patch(self, *args, **kwargs):
        sleep(self.delay)
        return requests.patch(*args, **kwargs)

    @wraps(requests.delete)
    def delete(self, *args, **kwargs):
        sleep(self.delay)
        return requests.delete(*args, **kwargs)

    @wraps(requests.head)
    def head(self, *args, **kwargs):
        sleep(self.delay)
        return requests.head(*args, **kwargs)

    @wraps(requests.options)
    def options(self, *args, **kwargs):
        sleep(self.delay)
        return requests.options(*args, **kwargs)

    @wraps(requests.request)
    def request(self, *args, **kwargs):
        sleep(self.delay)
        return requests.request(*args, **kwargs)
