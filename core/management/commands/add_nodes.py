import time
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum, Max

from core import models
from core.manager.base import Manager

class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 60 * 1

    help = 'Add nodes'

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
            help='С какой периодичностью запускать проверку (в секундах)',
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
            not_started_nodes = models.Node.get_not_started_nodes(region)

            # If there are nodes that are not running - wait
            if not_started_nodes.exists():
                if self.verbosity:
                    print(f'There are no running nodes ({not_started_nodes.count()}), wait ...')
                return

            # If there are no nodes in the region, we add
            if not running_nodes.exists():
                if self.verbosity:
                    print(f'Node does in region {region}')
                self.add_nodes(region)
                return

            load_sum = 0
            for node in running_nodes:
                load_sum += node.get_load()

            throughput_sum = running_nodes.aggregate(throughput_sum=Sum('throughput'))['throughput_sum'] or 1
            load_average = (load_sum / throughput_sum) * 100

            if load_average >= settings.MAX_LOAD_AVERAGE:
                if self.verbosity:
                    print(f'Load increased ({load_average}%), add nodes ...')
                self.add_nodes(region)

    def add_nodes(self, region: str):
        manager = Manager.get_manager()
        for _ in range(settings.NODE_BUNCH_SIZE):
            last_id = models.Node.objects.aggregate(max_id=Max('id'))['max_id'] or 1
            node  = models.Node(name=f'{region}{last_id + 1}', region=region)
            manager.start(node)

            if self.verbosity:
                print(f'Add node {node.name} in region {region}')
