import abc

from collections import Counter

class ResponseHandler(abc.ABC):

    @abc.abstractmethod
    def handle_response(self, res):
        pass

class CounterHandler(ResponseHandler):
    def __init__(self):
        self.counter=Counter()

    def handle_response(self, res):
        self.counter[res.status] += 1

    def print_stats(self):
        for k,v in self.counter.items():
            print(k,': ',v)
