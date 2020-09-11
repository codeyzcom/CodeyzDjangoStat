import time

from cdzstat.poller import Poller


class StatCollector:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()

        start_time = time.time()
        response = self.get_response(request)
        middle_time = time.time()

        poller = Poller(request, response)
        poller.execute()

        end_time = time.time()

        print(f'\nPATH: {request.path}\nELAPSED: {end_time - start_time},\nRESP: {middle_time - start_time}\nCDZ: {end_time - middle_time}')
        return response
