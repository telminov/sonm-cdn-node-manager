import datetime
from typing import List


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
