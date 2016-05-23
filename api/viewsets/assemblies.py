from rest_framework import viewsets

from api.serializers.assemblies import AssemblyStatSerializer, ContigSerializer
from assembly.models import Stats, Contigs


class AssemblyViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembly stats."""

    queryset = Stats.objects.all()
    serializer_class = AssemblyStatSerializer


class ContigViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembled contigs."""

    queryset = Contigs.objects.all()
    serializer_class = ContigSerializer
