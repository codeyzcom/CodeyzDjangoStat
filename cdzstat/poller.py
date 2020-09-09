from cdzstat import handlers


class Poller:

    def __init__(self, request, response):
        self._req = request
        self._resp = response
        self.handler_set = []

    def execute(self):
        print(self._req.path)
        if self._req.path == '/cdzstat/collect_statistic':
            self.handler_set = _prepare_cdzstat_js_script_handlers()
        else:
            self.handler_set = self._prepare_std_handlers()

        sorted_handlers = sorted(self.handler_set, key=lambda k: k.priority)

        for handler in sorted_handlers:
            obj = handler(self._req, self._resp)
            if obj.preprocessing():
                obj.process()
            else:
                print(f'Hanlder.process for {obj.__class__} skip!')

    def _prepare_std_handlers(self) -> list:
        return [
            handlers.SessionHandler,
            handlers.PermanentSessionHandler,
            handlers.IpAddressHandler,
            handlers.UserAgentHandler,
            handlers.HttpHeadersHandler,
        ]

    def _prepare_cdzstat_js_script_handlers(self) -> list:
        return []
