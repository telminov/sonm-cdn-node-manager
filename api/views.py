from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class Nodes(GenericAPIView):

    def get(self, request):
        return Response({"europe": ["127.0.0.1"]})