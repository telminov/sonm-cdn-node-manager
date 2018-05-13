import datetime
from typing import List

CND_NODE_IMAGE_NAME = 'redis:3.0.7'     # FIXME


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
