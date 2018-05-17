from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

import core.models
from api import serializers


class NodesByRegions(GenericAPIView):
    def get(self, request):
        nodes_by_regions = {}

        qs = core.models.Node.objects\
            .filter(deleted__isnull=True)\
            .exclude(ip4='')

        for node in qs.iterator():
            nodes_by_regions.setdefault(node.region, []).append(node.ip4)

        return Response(nodes_by_regions)


class Node(ModelViewSet):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = core.models.Node.objects.all()
    serializer_class = serializers.Node
