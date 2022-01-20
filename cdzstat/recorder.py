class Recorder:

    def __init__(self, request, response):
        self._context = {
            'request': request,
            'response': response,
        }

    def execute(self):
        pass
