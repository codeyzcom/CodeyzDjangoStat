import logging

from cdzstat import handlers

logger = logging.getLogger()


class Poller:

    def __init__(self, request, response):
        self.handler_set = []
        self. ctx = {
            'state': True,
            'request': request,
            'response': response,
            'request_data': {},
            'session_data': {}
            }

    def execute(self):
        if self.ctx.get('request').path_info == '/cdzstat/collect_statistic':
            self.handler_set = self._prepare_script_handlers()
            self.ctx['kind'] = 'script'
        else:
            self.handler_set = self._prepare_native_handlers()
            self.ctx['kind'] = 'native'

        sorted_handlers = sorted(self.handler_set, key=lambda k: k.priority)

        for handler in sorted_handlers:
            obj = handler(self.ctx)
            if self.ctx.get('state'):
                if obj.preprocessing():
                    obj.process()
                else:
                    logger.warning(
                        'Hanlder.process for %s skip!', obj.__class__
                        )
            else:
                logger.warning('Stop perform!')
                break

    def _prepare_native_handlers(self) -> list:
        return [
            handlers.StoreHandler,
            handlers.TimestampNativeHandler,
            handlers.RequestSetterHandler,
            handlers.SessionGetterHandler,
            handlers.SessionSetterHandler,
            handlers.SessionUpdateHandler,
            handlers.PermanentSessionHandler,
            handlers.IpAddressHandler,
            handlers.UserAgentHandler,
            handlers.TimestampNativeHandler,
            handlers.HttpHeadersHandler,
            handlers.NodeNativeHandler,
            handlers.TransitionNativeHandler,
            handlers.AdjacencyHandler,
            handlers.RequestSizeHandler,
            handlers.ResponseSizeHandler
        ]

    def _prepare_script_handlers(self) -> list:
        return [
            handlers.ScriptInitHandler,
            handlers.StoreHandler,
            handlers.RequestGetterHandler,
            handlers.SessionGetterHandler,
            handlers.PermanentSessionHandler,
            handlers.IpAddressHandler,
            handlers.UserAgentHandler,
            handlers.NodeScriptHandler,
            handlers.TransitionScriptHandler,
            handlers.AdjacencyHandler,
            handlers.AdvancedParamScriptHandler,
            handlers.TimestampScriptHandler,
        ]
