import multiprocessing as mp

from django.core.management.base import BaseCommand

from cdzstat import workers


class Command(BaseCommand):
    help = 'Run statistics collection worker - CodeyzDjangoStat'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        rq_worker = mp.Process(target=workers.run_rq_worker)
        session_worker = mp.Process(target=workers.SessionWorker().run)

        rq_worker.start()
        session_worker.start()
