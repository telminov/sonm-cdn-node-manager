from typing import List
from django.conf import settings
from core.models import Node

CND_NODE_IMAGE_NAME = 'telminov/sonm-cdn-node'


class Manager:
    @staticmethod
    def get_manager() -> 'Manager':
        if settings.USE_DO:
            from core.manager.do import DOManager
            return DOManager()
        else:
            from core.manager.sonm import SonmManager
            return SonmManager()

    def start(self, node: Node):
        raise NotImplementedError()

    def destroy(self, node: Node):
        raise NotImplementedError()

    def refresh(self, verbose: bool = False):
        """refresh nodes state info (ip, load)"""
        raise NotImplementedError()

    def init_regions(self) -> List[Node]:
        """Инициализация сети с нодами"""
        nodes = []

        for region in Node.REGIONS:
            node = Node(name='%s1' % region, region=region)
            self.start(node)
            nodes.append(node)

        return nodes
