from django.core.management.base import BaseCommand, CommandError

from cdzstat import workers


class Command(BaseCommand):
    help = 'Run statistics collection worker - CodeyzDjangoStat'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        worker = workers.SessionWorker()
        worker.run()
