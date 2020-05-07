import time

from .services import (
    ExceptionService,
    LowLevelService,
)


class StatCollector:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()
        response = self.get_response(request)

        exc_srv = ExceptionService(request)
        if not exc_srv.check():
            lls = LowLevelService(request, response)
            lls.process()
        else:
            print(
                f'The path {request.path} will not be processed, '
                f'as it is added to the exceptions!'
            )

        return response
