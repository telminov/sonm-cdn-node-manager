from django.contrib import admin
from core import models


class Node(admin.ModelAdmin):
    search_fields = ('name', )
    list_filter = ('stopped', 'region', )
    list_display = ('name', 'region', 'ip4', 'created', 'started', 'heartbeat', 'stopped')
    actions = ['stop_nodes']

    def stop_nodes(self, request, queryset):
        for node in queryset.iterator():
            node.stop()


admin.site.register(models.Node, Node)

