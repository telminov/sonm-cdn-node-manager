import datetime
import logging
from typing import List
from docker.client import DockerClient
from docker.models.services import Service as SwarmService

from .base import Task, Manager, CND_NODE_IMAGE_NAME


# Предполагается, что настроен swarm:
# - машина, на которой работает SwarmManager является менеджером swarm
# - есть swarm-ноды со всеми возможными значениями region


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class SwarmTask(Task):
    def __init__(self, name: str, region: str, created: datetime.datetime):
        super().__init__(name, region, created)
        self.service = None


class SwarmManager(Manager):

    def __init__(self, tasks: List[Task] = None):
        super().__init__(tasks)
        self.docker_client = DockerClient()

    def create(self, name: str, region: str) -> SwarmTask:
        task = SwarmTask(name=name, region=region, created=datetime.datetime.now())

        # если в этом регионе таски есть - скейлим, в противном случае создаем
        swarm_service = self._get_swarm_service(region)
        if swarm_service:
            new_tasks_count = len(swarm_service.tasks()) + 1
            swarm_service.scale(new_tasks_count)
        else:
            swarm_service = self.docker_client.services.create(
                name=name,
                image=CND_NODE_IMAGE_NAME,
                constraints=['node.labels.type == %s' % region]
            )

        swarm_service.reload()
        task.service = swarm_service
        return task

    def stop(self, task: SwarmTask):
        new_tasks_count = len(task.service.tasks()) - 1

        # если в этом регионе таски есть - скейлим, в противном случае удаляем
        swarm_service = self._get_swarm_service(task.region)
        if new_tasks_count > 0:
            swarm_service.scale(new_tasks_count)
            swarm_service.reload()
        else:
            task.service.remove()

        task_index = self.tasks.index(task)
        self.tasks.pop(task_index)

    def _get_swarm_service(self, region: str) -> SwarmService:
        for task in self.tasks:
            if task.region == region:
                return task.service
