import time
from django.core.management.base import BaseCommand

from core.manager.base import Manager


class Command(BaseCommand):

    def handle(self, *args, **options):
        manager = Manager.get_manager()
        manager.init_regions()
