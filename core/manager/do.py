# Digital Ocean
import random
from typing import List
import digitalocean
from django.conf import settings
from django.utils.timezone import now

from .base import Manager
from core.models import Node


REGIONS_MAP = {
    'AF': ['blr1', 'tor1'],                             # Африка - Бангалор, Торонто
    'AN': ['ams3'],                                     # Антарктика - Амстердам
    'AS': ['sgp1'],                                     # Азия - Сингапур
    'EU': ['fra1', 'lon1'],                             # Европа - Франкфурд, Лондон
    'NA': ['nyc1', 'nyc3',  'sfo2'],                    # Северная Америка
    'OC': ['sgp1'],                                     # Океания - Сингапур
    'SA': ['sfo2'],                                     # Южная Америка
}
TAG_NAME = 'sonm-cdn'


class DOManager(Manager):

    def __init__(self):
        super().__init__()
        self._manager = None
        self._image = None
        self._keys = []

    def start(self, node: Node):
        size_slug = 's-1vcpu-1gb'
        ssh_keys = self.get_ssh_keys()
        do_region = random.choice(REGIONS_MAP[node.region])

        droplet = digitalocean.Droplet(token=settings.DO_TOKEN,
                                       name=node.name,
                                       region=do_region,
                                       image=self.get_image(),
                                       size_slug=size_slug,
                                       ssh_keys=ssh_keys,
                                       tags=[TAG_NAME],
                                       backups=False)
        droplet.create()

        node.external_id = droplet.id
        node.throughput = 100     # let's consider that maximum throughput 100 Mb/sec
        node.save()

    def destroy(self, node: Node):
        node.stopped = now()
        node.save()

        for droplet in self.get_droplets():
            if str(droplet.id) == node.external_id:
                droplet.destroy()
                return

        raise Exception('Not found node with external ID "%s"' % node.external_id)

    def refresh(self):
        current_nodes = {n.external_id: n for n in Node.objects.filter(stopped__isnull=True)}

        droplets = self.get_droplets()
        for droplet in droplets:
            external_id = str(droplet.id)
            if external_id not in current_nodes:
                continue

            node = current_nodes.pop(external_id)
            node.ip4 = droplet.ip_address
            node.port = '80'
            node.heartbeat = now()
            if not node.started:
                node.started = now()
            node.save()

        # ноды, для которых не были найдены дроплеты
        for node in current_nodes.values():
            node.stopped = now()
            node.save()

    def get_manager(self) -> digitalocean.Manager:
        if not self._manager:
            self._manager = digitalocean.Manager(token=settings.DO_TOKEN)
        return self._manager

    def get_ssh_keys(self) -> List[digitalocean.SSHKey]:
        if not self._keys:
            for key in self.get_manager().get_all_sshkeys():
                if key.name in settings.DO_SSH_KEY_NAMES:
                    self._keys.append(key)
            if not self._keys:
                raise Exception('SSH keys "%s" not found' % settings.DO_SSH_KEY_NAMES)
        return self._keys

    def get_droplets(self) -> List[digitalocean.Droplet]:
        droplets = self.get_manager().get_all_droplets(tag_name=TAG_NAME)
        return droplets

    def get_image(self) -> digitalocean.Image:
        if not self._image:
            for image in self.get_manager().get_all_images():
                if image.name == settings.CND_NODE_IMAGE_NAME:
                    self._image = image
                    break
            if not self._image:
                raise Exception('Digital Ocean image "%s" not found' % settings.CND_NODE_IMAGE_NAME)
        return self._image
