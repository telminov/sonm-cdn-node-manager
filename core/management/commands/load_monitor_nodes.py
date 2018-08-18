import time
import requests

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from core import models

class Command(BaseCommand):
    DEFAULT_SLEEP_TIME = 10 * 1

    help = 'Load monitor nodes'

    sleep_time = None

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

        if options.get('infinitely'):
            while True:
                self.monitor()
                time.sleep(self.sleep_time)
        else:
            self.monitor()

    def monitor(self):
        nodes = models.Node.get_running_nodes()
        for node in nodes.iterator(100):
            self.check_node(node)

    @staticmethod
    def check_node(node: models.Node):
        node_address = node.get_address()
        try:
            response = requests.get(f'http://{node_address}/bytes_sent')
            if response.status_code < 300:
                node.prev_sent_bytes = node.last_sent_bytes
                node.prev_sent_bytes_dt = node.last_sent_bytes_dt
                node.last_sent_bytes = int(response.content)
                node.last_sent_bytes_dt = now()
                node.save()
            else:
                print(f'Ошибка проверки загруженности ноды {node.id} с адрессом {node_address}.')
                print(f'КОД: {response.status_code}')
                print(f'ОТВЕТ: {response.content}')

        except Exception as e:
            print(f'Ошибка проверки загруженности ноды {node.id} с адрессом {node_address}')
            print(e)
