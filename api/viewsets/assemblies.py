from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.assemblies import (
    AssemblyStatSerializer,
    ContigSerializer,
    ContigFullSerializer
)
from assembly.models import Stats, Contigs


class AssemblyViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembly stats."""

    queryset = Stats.objects.all()
    serializer_class = AssemblyStatSerializer


class ContigViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembled contigs."""

    queryset = Contigs.objects.all()
    serializer_class = ContigSerializer

    def retrieve(self, request, pk=None):
        queryset = None
        serializer = None
        if pk:
            queryset = Contigs.objects.get(pk=pk)
            serializer = ContigFullSerializer(queryset)
        else:
            queryset = Contigs.objects.all()
            serializer = ContigSerializer(queryset)

        return Response(serializer.data)
