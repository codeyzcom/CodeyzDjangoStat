from .services import ExceptionService


class StatCollector:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        exc_srv = ExceptionService(request)
        if not exc_srv.check():
            pass
        else:
            print(
                f'The path {request.path} will not be processed, '
                f'as it is added to the exceptions!'
            )

        return response
