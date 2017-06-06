from rest_framework.response import Response
from rest_framework.decorators import list_route

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.assemblies import get_assembly_stats
from api.serializers.assemblies import (
    AssemblyStatSerializer,
    ContigSerializer,
    ContigFullSerializer
)
from api.validators import validate_list_of_ids

from assembly.models import Stats, Contigs


class AssemblyViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembly stats."""

    queryset = Stats.objects.all()
    serializer_class = AssemblyStatSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return assembly info for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                scaffolds = 'TRUE' if 'scaffolds' in request.GET else 'FALSE'
                plasmids = 'TRUE' if 'plasmids' in request.GET else 'FALSE'
                return self.formatted_response(get_assembly_stats(
                    request.data['ids'],
                    is_scaffolds=scaffolds,
                    is_plasmids=plasmids
                ))


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
