import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta

from core import models


class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 10 * 1

    help = 'Destroy stopped nodes'

    sleep_time = None
    verbosity = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            dest='infinitely',
            action='store_true',
            help=u'Бесконечный цикл, смотрим на загрузку нод',
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
                time.sleep(self.sleep_time)
        else:
            self.delete_nodes()

    def destroy_nodes(self):
        nodes = self.get_need_destroy_nodes()
        nodes_count = nodes.count()

        for node in nodes:
            if self.verbosity:
                print(f'Нода {node.name} удалена')

            node.destroy()

        if self.verbosity and nodes_count:
            print(f'Было удалено {nodes_count} нод')

    @staticmethod
    def get_need_destroy_nodes():
        return models.Node.objects.filter(stopped__lte=now() - timedelta(minutes=settings.DESTROY_NODES_TIME))
