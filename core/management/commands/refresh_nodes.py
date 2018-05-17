import time
from django.core.management.base import BaseCommand

from core.manager.base import Manager


class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 60 * 1
    help = 'Refresh nodes state'

    def add_arguments(self, parser):
        parser.add_argument(
            '--infinitely',
            dest='infinitely',
            action='store_true',
            help=u'Бесконечный цикл, смотрим на изменения нод',
        )
        parser.add_argument(
            '--time',
            dest='time',
            type=int,
            help=u'С какой периодичностью запускать проверку (в секундах)',
        )

    def handle(self, *args, **options):
        self.sleep_time = options.get('time') or self.DEFAULT_SLEEP_TIME
        manager = Manager.get_manager()

        if options.get('infinitely'):
            while True:
                manager.refresh()
                time.sleep(self.sleep_time)
        else:
            manager.refresh()
