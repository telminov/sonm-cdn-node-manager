# Digital Ocean
import random
from typing import List
import digitalocean
from django.conf import settings

from .base import Manager
from core.models import Node


REGIONS_MAP = {
    'AF': ['blr1', 'tor1'],                             # Африка - Бангалор, Торонто
    'AN': ['ams2', 'ams3'],                             # Антарктика - Амстердам
    'AS': ['sgp1'],                                     # Азия - Сингапур
    'EU': ['fra1', 'lon1'],                             # Европа - Франкфурд, Лондон
    'NA': ['nyc1', 'nyc2', 'nyc3', 'sfo1', 'sfo2'],     # Северная Америка
    'OC': ['sgp1'],                                     # Океания - Сингапур
    'SA': ['sfo1'],                                     # Южная Америка
}
TAG_NAME = 'sonm-cdn'


class DOManager(Manager):

    def __init__(self):
        super().__init__()
        self._manager = None
        self._keys = []

    def start(self, node: Node):
        size_slug = 's-1vcpu-1gb'
        ssh_keys = self.get_ssh_keys()
        do_region = random.choice(REGIONS_MAP[node.region])

        droplet = digitalocean.Droplet(token=settings.DO_TOKEN,
                                       name=node.name,
                                       region=do_region,
                                       image='ubuntu-18-04-x64',    # TODO: заменить на образ с нодой CDN
                                       size_slug=size_slug,
                                       ssh_keys=ssh_keys,
                                       tags=[TAG_NAME],
                                       backups=False)
        droplet.create()

        node.external_id = droplet.id
        node.save()

    def stop(self, node: Node):
        for droplet in self.get_droplets():
            if str(droplet.id) == node.external_id:
                droplet.destroy()
                return
        raise Exception('Not found node with external ID "%s"' % node.external_id)

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
