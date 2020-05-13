import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from cdzstat import (
    REDIS_CONN,
    services,
)

_executor = ThreadPoolExecutor(5)


class SessionWorker:

    def __init__(self):
        pass

    def run(self):
        ps = REDIS_CONN.pubsub()
        ps.subscribe('one')

        loop = asyncio.get_event_loop()

        while True:
            message = ps.get_message()
            if message:
                data_handle_task = loop.create_task(
                    SessionWorker._wrapper(loop, message.get('data'))
                )
                loop.run_until_complete(data_handle_task)
            time.sleep(0.1)

    @staticmethod
    async def _wrapper(loop, data):
        data_handler = services.DataHandlerService(data)
        await loop.run_in_executor(_executor, data_handler.process)
