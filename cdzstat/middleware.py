import time

from cdzstat.recorder import Recorder


class StatCollector:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()

        response = self.get_response(request)

        recorder = Recorder(request, response)
        recorder.execute()

        end_time = time.time()

        print(f'\n{request.path}  {end_time - request.start_time}')
        return response
