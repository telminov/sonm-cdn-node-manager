from django.db import models
from django.utils.timezone import now


class Node(models.Model):
    # простое деление по континентам. Можно сделать лучше через координаты.
    # REGIONS = ('AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA')
    REGIONS = ('main', )    # пока SONM не поддерживает регионы
    REGIONS_CHOICES = [(r, r) for r in REGIONS]

    external_id = models.CharField(max_length=255, null=True, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, choices=REGIONS_CHOICES)
    ip4 = models.CharField(max_length=15, blank=True)
    port = models.CharField(max_length=5, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, blank=True)
    heartbeat = models.DateTimeField(null=True, blank=True)
    stopped = models.DateTimeField(null=True, blank=True)

    throughput = models.BigIntegerField(blank=True, null=True,
                                        help_text='Maximum bandwidth of the host. Mb/sec')
    prev_sent_bytes = models.BigIntegerField(blank=True, null=True,
                                             help_text='Previous measurement of the amount of traffic sent from the host')
    prev_sent_bytes_dt = models.DateTimeField(blank=True, null=True,
                                              help_text='Previous measurement time')
    last_sent_bytes = models.BigIntegerField(blank=True, null=True,
                                             help_text='Last measure of the amount of traffic sent from the host')
    last_sent_bytes_dt = models.DateTimeField(blank=True, null=True,
                                              help_text='Last measurement time')

    def __str__(self):
        return self.name

    def stop(self):
        if self.stopped:
            return

        self.stopped = now()
        self.save()

    def destroy(self):
        from core.manager.base import Manager
        manager = Manager.get_manager()

        manager.stop(self)
        self.delete()

    def get_address(self):
        if self.ip4:
            return '%s:%s' % (self.ip4, self.port)

    def get_load(self):
        load = 0
        if self.prev_sent_bytes and self.last_sent_bytes:
            seconds = (self.last_sent_bytes_dt - self.prev_sent_bytes_dt).seconds
            load = (self.last_sent_bytes - self.prev_sent_bytes) / seconds
            load = load  / (1024 ^ 2)

        return load

    @classmethod
    def get_running_nodes(cls, region=None):
        nodes = cls.objects.filter(started__isnull=False, stopped__isnull=True)
        if region:
            nodes = nodes.filter(region=region)

        return nodes

    @classmethod
    def get_not_started_nodes(cls, region=None):
        nodes = cls.objects.filter(started__isnull=True)
        if region:
            nodes = nodes.filter(region=region)

        return nodes


class SonmBid(models.Model):
    node = models.OneToOneField(Node, on_delete=models.CASCADE, related_name='bid')
    deal_id = models.CharField(blank=True, max_length=100)
    task_id = models.CharField(blank=True, max_length=100)
