from django.db import models
from django.utils.timezone import now


class Node(models.Model):
    # простое деление по континентам. Можно сделать лучше через координаты.
    REGIONS = ('AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA')
    REGIONS_CHOICES = [(r, r) for r in REGIONS]

    external_id = models.CharField(max_length=255, null=True, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, choices=REGIONS_CHOICES)
    ip4 = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, blank=True)
    heartbeat = models.DateTimeField(null=True, blank=True)
    stopped = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def stop(self):
        if self.stopped:
            return

        from core.manager.base import Manager
        manager = Manager.get_manager()
        manager.stop(self)

        self.stopped = now()
        self.save()
