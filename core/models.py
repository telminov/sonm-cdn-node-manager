from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=100)
    ip4 = models.CharField(max_length=15, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    heartbeat = models.DateTimeField(null=True)
    deleted = models.DateTimeField(null=True)
