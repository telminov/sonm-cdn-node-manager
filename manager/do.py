# Digital Ocean
import datetime
from typing import List
from django.conf import settings
from django.utils.timezone import now

from .base import Task, Manager
import digitalocean


REGIONS_MAP = {
    'AF': ['blr1', 'tor1'],                             # Африка - Бангалор, Торонто
    'AN': ['ams2', 'ams3'],                             # Антарктика - Амстердам
    'AS': ['sgp1'],                                     # Азия - Сингапур
    'EU': ['fra1', 'lon1'],                             # Европа - Франкфурд, Лондон
    'NA': ['nyc1', 'nyc2', 'nyc3', 'sfo1', 'sfo2'],     # Северная Америка
    'OC': ['sgp1'],                                     # Океания - Сингапур
    'SA': ['sfo1'],                                     # Южная Америка
}


class DOTask(Task):
    def __init__(self, name: str, region: str, created: datetime.datetime, droplet: digitalocean.Droplet):
        super().__init__(name, region, created)
        self.droplet = droplet


class DOManager(Manager):

    def __init__(self):
        super().__init__()
        self._manager = None
        self._key = []

    def create(self, name: str, region: str) -> DOTask:
        size_slug = 's-1vcpu-1gb'

        do_region = REGIONS_MAP[region]
        droplet = digitalocean.Droplet(token=settings.DO_TOKEN,
                                       name=name,
                                       region=do_region,
                                       image='ubuntu-18-04-x64',    # TODO: заменить на образ с нодой CDN
                                       size_slug=size_slug,
                                       ssh_keys=self.get_ssh_keys(),
                                       backups=False)
        droplet.create()
        task = DOTask(name=name, region=region, created=now(), droplet=droplet)
        return task

    def stop(self, task: Task):
        pass

    def get_manager(self) -> digitalocean.Manager:
        if not self._manager:
            self._manager = digitalocean.Manager(token=settings.DO_TOKEN)
        return self._manager

    def get_ssh_keys(self) -> List[digitalocean.SSHKey]:
        if not self._key:
            for key in self.get_manager().get_all_sshkeys():
                if key.name == settings.DO_SSH_KEY_NAMES:
                    self._key.append(key)
            if not self._key:
                raise Exception('SSH keys "%s" not found' % settings.DO_SSH_KEY_NAMES)
        return self._key
