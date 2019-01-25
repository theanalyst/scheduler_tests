import abc

from collections import Counter

class ResponseHandler(abc.ABC):

    @abc.abstractmethod
    def handle_response(self, response, response_data):
        pass

    def needs_data(self):
        return False

class CounterHandler(ResponseHandler):
    '''
    A very basic request status counter, aggregating the total requests per
    status code:
    Final output is just a simple printout of status: aggr count
    '''

    def __init__(self):
        self.counter=Counter()

    def handle_response(self, response, *_):
        self.counter[response.status] += 1

    def print_stats(self):
        for k,v in self.counter.items():
            print(k,': ',v)
