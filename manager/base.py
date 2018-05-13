import datetime
from typing import List

CND_NODE_IMAGE_NAME = 'redis:3.0.7'     # FIXME

# простое деление по континентам. Можно сделать лучше через координаты.
REGIONS = ('AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA', 'DEFAULT')


class Task:
    def __init__(self, name: str, region: str, created: datetime.datetime):
        self.name = name
        self.region = region
        self.created = created


class Manager:

    def __init__(self, tasks: List[Task] = None):
        self.tasks = tasks or []

    def create(self, name: str, region: str) -> Task:
        raise NotImplementedError()

    def stop(self, task: Task):
        raise NotImplementedError()

    def init_regions(self) -> List[Task]:
        """Инициализация сети с нодами"""
        tasks = []

        for region in REGIONS:
            task = self.create(name='node', region=region)
            tasks.append(task)

        return tasks
