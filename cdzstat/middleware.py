import time

from .services import LowLevelService


class StatCollector:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()
        response = self.get_response(request)

        lls = LowLevelService(request, response)
        lls.process()

        return response
