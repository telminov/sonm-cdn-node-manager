from django.contrib import admin
from core import models


class Node(admin.ModelAdmin):
    search_fields = ('name', )
    list_filter = ('region', )


admin.site.register(models.Node, Node)

