import time

from .services import (
    ExceptionService,
    LowLevelService,
    CollectorService,
)


class StatCollector:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.start_time = time.time()
        response = self.get_response(request)

        exc_srv = ExceptionService(request)
        if not exc_srv.check():
            collector_service = CollectorService(request, response)
            collector_service.low_level_collector()
            collector_service.process()
        else:
            print(
                f'The path {request.path} will not be processed, '
                f'as it is added to the exceptions!'
            )

        return response
