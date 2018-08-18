import time
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum

from core import models
from core.manager.base import Manager

class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 60 * 1

    help = 'Add nodes'

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
         # Собираем метрики и принимаем решение о добавлении или удалении нод

        nodes = models.Node.objects.filter(stopped__isnull=True).exclude(ip4='')
        for region in set(nodes.values_list('region', flat=True)):
            running_nodes = models.Node.get_running_nodes(region)
            not_started_nodes = models.Node.get_not_started_nodes(region)

            # есть нод, которые не стартанули - ждем
            if not_started_nodes.exists():
                if self.verbosity:
                    print(f'Есть не запустившиеся ноды ({not_started_nodes.count()} шт), ждем')
                return

            # Если нет нод в регионе - добавим
            if not running_nodes.exists():
                if self.verbosity:
                    print('Нет нод вообще, добавляем')
                self.add_nodes(region)
                return

            nodes_info = running_nodes.aggregate(
                throughput_sum=Sum('throughput'),
                last_sent_bytes_sum = Sum('last_sent_bytes')
            )

            throughput_sum = nodes_info['throughput_sum'] or 0
            last_sent_bytes_sum = nodes_info['last_sent_bytes_sum'] or 0
            load_average = (last_sent_bytes_sum / throughput_sum) * 100

            if load_average >= settings.MAX_LOAD_AVERAGE:
                if self.verbosity:
                    print(f'Нагрузка выросла ({load_average}%), добавляем')
                self.add_nodes(region)

    def add_nodes(self, region: str):
        manager = Manager.get_manager()
        for _ in range(settings.NODE_BUNCH_SIZE or 1):
            node  = models.Node(name=f'{region} - {uuid.uuid4()}', region=region)
            manager.start(node)

            if self.verbosity:
                print(f'Добавлена нода с именем {node.name} в регионе {region}')
