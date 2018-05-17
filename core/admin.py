from django.contrib import admin
from core import models


class Node(admin.ModelAdmin):
    search_fields = ('name', )
    list_filter = ('region', )
    list_display = ('name', 'region', 'ip4', 'created', 'started', 'heartbeat', 'deleted')


admin.site.register(models.Node, Node)

