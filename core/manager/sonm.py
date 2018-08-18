from typing import Tuple

from django.conf import settings
from django.utils.timezone import now

from sonm.bid import BidParams, NetworkParams, Benchmarks
from sonm.task import TaskParams
from sonm.customer import Customer
import sonm.consts

from .base import Manager
from core import models


class SonmManager(Manager):
    def __init__(self):
        super().__init__()
        self.sonm = Customer()

    def start(self, node: models.Node):
        b = Benchmarks(
            ram_size=1024 * 1024 * 100,             # 100MB
            storage_size=1024 * 1024 * 1024 * 10,   # 10GB
            cpu_cores=1,
            cpu_sysbench_multi=1000,
            cpu_sysbench_single=800,
            net_download=1024 * 1024 * settings.NODE_DOWNLOAD,
            net_upload=1024 * 1024 * settings.NODE_UPLOAD,
        )
        n = NetworkParams(incoming=True, outbound=True, overlay=True)
        bid = BidParams(
            duration=0,
            price='0.01 USD/h',
            counterparty=settings.COUNTERPARTY,
            identity=sonm.consts.IDENTITY_ANONYMOUS,
            tag='sonm-cdn-node',
            benchmarks=b,
            network=n,
        )

        bid_id = self.sonm.order.create(bid=bid)['id']

        node.external_id = bid_id
        node.throughput = b.net_upload
        node.save()

        models.SonmBid.objects.create(node=node)

    def stop(self, node: models.Node):
        node.stopped = now()
        node.save()

        if node.bid.deal_id:
            self.sonm.deal.close(deal_id=node.bid.deal_id)
        else:
            self.sonm.order.cancel(order_id=node.external_id)

    def refresh(self, verbose: bool = True):
        """refresh nodes state info (ip, load)"""
        deals = self.sonm.deal.list()['deals'] or []
        if verbose:
            print('Deals count: %s.' % len(deals))

        # refresh deals info
        deal_ids = set()
        for deal in deals:
            if verbose:
                print('Process deals %s.' % deal)

            deal_id = deal['id']
            deal_ids.add(deal_id)

            bid_id = deal.get('bidID')
            if not bid_id:
                continue

            # not relevant bid deal
            node_qs = models.Node.objects.filter(external_id=bid_id, stopped__isnull=True)
            if not node_qs.exists():
                self.sonm.deal.close(deal_id)
                continue
            node = node_qs[0]

            # deal ready for start task
            tasks = self.sonm.task.list(deal_id) or {}
            tasks = {task_id: info for task_id, info in tasks.items() if info['status'] <= 3}   # only active tasks
            if tasks:
                task_id = list(tasks.keys())[0]
            else:
                if verbose:
                    print('New deal. Starting task...' % deal)

                task_id = self._start_task(deal_id)
                node.started = now()

            node.heartbeat = now()
            node.save()

            # save task id
            if not node.bid.deal_id:
                node.bid.deal_id = deal_id
                node.bid.task_id = task_id
                node.bid.save()

                node.ip4, node.port = self._get_task_address(deal_id, task_id)
                node.save()

                if verbose:
                    print('Got address: %s' % node.get_address())

        # node had deal, but now no active deal (case of external deal closing)
        nodes_without_deal = models.Node.objects\
            .exclude(bid__deal_id__in=deal_ids) \
            .filter(stopped__isnull=True) \
            .exclude(bid__deal_id='')

        if verbose and nodes_without_deal.count():
            print('Nodes without deals: %s' % list(nodes_without_deal))

        nodes_without_deal.update(stopped=now())

    def _start_task(self, deal_id: str) -> str:
        params = TaskParams(
            image='telminov/sonm-cdn-node',
            expose=[(settings.NODE_EXPOSE_PORT, '80')],
            evn={'CMS_URL': settings.CMS_URL},
        )

        task_id = self.sonm.task.start(deal_id=deal_id, params=params)['id']
        return task_id

    def _get_task_address(self, deal_id: str, task_id: str) -> Tuple[str, str]:
        endpoints = self.sonm.task.status(deal_id=deal_id, task_id=task_id)['ports']['80/tcp']['endpoints']
        endpoint = [i for i in endpoints if not i['addr'].startswith('172.')][0]
        address = endpoint['addr']
        port = endpoint['port']
        return address, port
