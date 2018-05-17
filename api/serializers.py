from rest_framework import serializers
from core import models


class Node(serializers.ModelSerializer):
    class Meta:
        model = models.Node
        fields = '__all__'
