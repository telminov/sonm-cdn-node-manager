from django.core.management.base import BaseCommand

from core.manager.do import DOManager, REGIONS_MAP


class Command(BaseCommand):
    help = 'Distributes a CDN node image between Digital Ocean regions. ' \
           'It is enough to have it initially only in one region.'

    def handle(self, *args, **options):
        manager = DOManager()
        image = manager.get_image()

        do_regions = set()

        for region in REGIONS_MAP.keys():
            do_regions.update(REGIONS_MAP[region])

        for do_region in do_regions:
            if do_region not in image.regions:
                image.transfer(do_region)
