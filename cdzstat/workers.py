import time

from rq import Connection, Worker, Queue

from cdzstat import services


def run_rq_worker():
    with Connection():
        qs = ['default']
        w = Worker(qs)
        w.work()


class SessionWorker:

    def __init__(self):
        pass

    def run(self):
        s_gc = services.SessionGarbageCollectorService()
        while True:
            s_gc.execute()
            time.sleep(1)
