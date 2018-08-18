from rest_framework import serializers
from core import models


class Node(serializers.ModelSerializer):
    load = serializers.SerializerMethodField(method_name='get_load')

    class Meta:
        model = models.Node
        fields = '__all__'

    def get_load(self, instance: models.Node):
        return instance.get_load()
