import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum

from core import models


class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 10 * 1

    help = 'Stopped nodes'

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
        self.verbosity = bool(options.get('verbosity'))

        if options.get('infinitely'):
            while True:
                self.check_load_average()
                if self.verbosity:
                    print(f'Sleep {self.sleep_time} sec')

                time.sleep(self.sleep_time)
        else:
            self.check_load_average()

    def check_load_average(self):
        for region in models.Node.REGIONS:
            running_nodes = models.Node.get_running_nodes(region)

            load_sum = 0
            for node in running_nodes:
                load_sum += node.get_load()

            throughput_sum = running_nodes.aggregate(throughput_sum=Sum('throughput'))['throughput_sum']
            load_average = 0
            if throughput_sum:
                load_average = (load_sum / throughput_sum) * 100

            if load_average < settings.MIN_LOAD_AVERAGE:

                if running_nodes.count() > settings.NODE_BUNCH_SIZE:
                    if self.verbosity:
                        print(f'Load decreased ({load_average}%), stopped')
                    self.stop_nodes(region)

                elif self.verbosity:
                    print(f'Minimum number of nodes in region {region}')


    def stop_nodes(self, region: str):
        nodes = models.Node.get_running_nodes(region)

        nodes = nodes.order_by('last_sent_bytes')[:settings.NODE_BUNCH_SIZE]
        for node in nodes:
            node.stop()
            print(f'Stop node {node.name} in region {region}')
