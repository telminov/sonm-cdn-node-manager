import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta

from core import models


class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 10 * 1

    help = 'Destroy stopped nodes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            dest='infinitely',
            action='store_true',
            help='Бесконечный цикл, смотрим на загрузку нод',
        )
        parser.add_argument(
            '--time',
            dest='time',
            type=int,
            help=u'С какой периодичностью запускать проверку (в секундах)',
        )

    def handle(self, *args, **options):
        self.sleep_time = options.get('time') or self.DEFAULT_SLEEP_TIME
        self.verbosity = bool(options.get('verbosity'))

        if options.get('infinitely'):
            while True:
                self.destroy_nodes()
                if self.verbosity:
                    print(f'Sleep {self.sleep_time} sec')

                time.sleep(self.sleep_time)
        else:
            self.destroy_nodes()

    def destroy_nodes(self):
        nodes = self.get_need_destroy_nodes()
        nodes_count = nodes.count()

        for node in nodes:
            if self.verbosity:
                print(f'Node {node.name} destroyed')

            node.destroy()

        if self.verbosity and nodes_count:
            print(f'{nodes_count} nodes has been deleted')

    @staticmethod
    def get_need_destroy_nodes():
        deadline = now() - timedelta(minutes=settings.DESTROY_NODES_TIME)
        return models.Node.objects.filter(stopped__lte=deadline)
