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
                self.monitor()
                if self.verbosity:
                    print(f'Sleep {self.sleep_time} sec')
                time.sleep(self.sleep_time)
        else:
            self.monitor()

    def monitor(self):
        nodes = models.Node.get_running_nodes()
        for node in nodes.iterator():
            self.check_node(node)

    def check_node(self, node: models.Node):
        node_address = node.get_address()
        try:
            response = requests.get(f'http://{node_address}/bytes_sent')
            if response.status_code < 300:
                node.prev_sent_bytes = node.last_sent_bytes
                node.prev_sent_bytes_dt = node.last_sent_bytes_dt
                node.last_sent_bytes = int(response.content)
                node.last_sent_bytes_dt = now()
                node.save()

                if self.verbosity:
                    print(f'Node {node.name}: {node.get_load()} Mb/sec')

            else:
                print(f'Node check load error! '
                      f'NAME: {node.id} '
                      f'ADDRESS: {node_address}.'
                      f'CODE: {response.status_code}'
                      f'RESPONSE: {response.content}\n')

        except Exception as e:
            print(f'Node check load error! '
                  f'NAME: {node.id} '
                  f'ADDRESS: {node_address}.'
                  f'EXCEPTION: \n{e}.\n')
