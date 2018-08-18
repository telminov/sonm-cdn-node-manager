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
            help='Infinite loop, look at the changes in the node',
        )
        parser.add_argument(
            '--time',
            dest='time',
            type=int,
            help='How often to run the check (in seconds)',
        )

    def handle(self, *args, **options):
        self.sleep_time = options.get('time') or self.DEFAULT_SLEEP_TIME
        verbosity = bool(options.get('verbosity'))
        manager = Manager.get_manager()

        if options.get('infinitely'):
            while True:
                manager.refresh(verbose=verbosity)

                if verbosity:
                    print('Sleep %s secs' % self.sleep_time)

                time.sleep(self.sleep_time)
        else:
            manager.refresh(verbose=verbosity)
