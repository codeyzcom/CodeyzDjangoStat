import time

from rq import Connection, Worker, Queue

from cdzstat import (
    REDIS_CONN,
    services,
    settings,
)


def run_rq_worker():
    with Connection():
        qs = ['default']
        w = Worker(qs)
        w.work()


class SessionWorker:

    def __init__(self):
        self.q = Queue(connection=REDIS_CONN)

    def run(self):
        ps = REDIS_CONN.pubsub()
        ps.subscribe(settings.CDZSTAT_QUEUE_SESSION)

        while True:
            message = ps.get_message()
            if message and message.get('type') == 'message':
                dhs = services.DataHandlerService(message.get('data'))
                self.q.enqueue(dhs.process, result_ttl=5)
            time.sleep(0.1)
