from rest_framework.response import Response
from rest_framework.decorators import list_route

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.assemblies import get_assembly_stats, get_assembly_contigs
from api.serializers.assemblies import (
    AssemblyStatSerializer,
    ContigSerializer,
    ContigFullSerializer
)
from api.validators import validate_list_of_ids
from api.utils import timeit

from assembly.models import Summary, Contig


class AssemblyViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembly stats."""

    queryset = Summary.objects.all()
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
                results, qt = timeit(
                    get_assembly_stats,
                    request.data['ids'],
                    request.user.pk,
                    is_plasmids=True if 'plasmids' in request.GET else False
                )
                return self.formatted_response(results, query_time=qt)


class ContigViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving assembled contigs."""

    queryset = Contig.objects.all()
    serializer_class = ContigSerializer

    def retrieve(self, request, pk=None):
        if pk:
            results, qt = timeit(
                get_assembly_contigs,
                [pk],
                request.user.pk,
                is_plasmids=True if 'plasmids' in request.GET else False,
                exclude_sequence=True if 'exclude_sequence' in request.GET else False,
            )
            return self.formatted_response(results, query_time=qt)
        else:
            queryset = Contig.objects.all()
            serializer = ContigSerializer(queryset)
            return Response(serializer.data)

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return assembly info for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            exclude_sequence = False
            if 'exclude_sequence' in request.GET:
                exclude_sequence = True
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                results, qt = timeit(
                    get_assembly_contigs,
                    request.data['ids'],
                    request.user.pk,
                    is_plasmids=True if 'plasmids' in request.GET else False,
                    exclude_sequence=exclude_sequence
                )
                return self.formatted_response(results, query_time=qt)
