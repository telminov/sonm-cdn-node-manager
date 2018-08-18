import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum

from core import models


class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 10 * 1
    MIN_LOAD_AVERAGE = 30  # в процентах
    MIN_NODES_COUNT = 1

    help = 'Stopped nodes'

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
                self.check_load_average()
                time.sleep(self.sleep_time)
        else:
            self.check_load_average()

    def check_load_average(self):
        nodes = models.Node.objects.filter(stopped__isnull=True).exclude(ip4='')
        for region in set(nodes.values_list('region', flat=True)):
            running_nodes = models.Node.get_running_nodes(region)

            nodes_info = running_nodes.aggregate(
                throughput_sum=Sum('throughput'),
                last_sent_bytes_sum=Sum('last_sent_bytes')
            )

            throughput_sum = nodes_info['throughput_sum'] or 0
            last_sent_bytes_sum = nodes_info['last_sent_bytes_sum'] or 0
            load_average = (last_sent_bytes_sum / throughput_sum) * 100

            if load_average < settings.MIN_LOAD_AVERAGE:

                # Если нод минимум, то пропустим
                if not running_nodes.exists() <= settings.NODE_BUNCH_SIZE:
                    if self.verbosity:
                        print('Минимальное количество нод')
                    return

                if self.verbosity:
                    print(f'Нагрузка снизилась ({load_average}%), убираем')

                self.stop_node(region)

    def stop_node(self, region: str):
        # Берем ноду, которая вообще не напрягается и стопаем ее

        nodes = models.Node.get_running_nodes(region)

        nodes = nodes.order_by('last_sent_bytes')[:settings.NODE_BUNCH_SIZE]
        for node in nodes:
            node.stop()
            print(f'Остановлена нода с именем {node.name} в регионе {region}')
