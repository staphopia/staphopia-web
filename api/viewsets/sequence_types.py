from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.sequence_types import MLSTSerializer, CGMLSTSerializer
from api.queries.sequence_types import (
    get_sequence_type,
    get_cgmlst,
    get_mlst_blast_results,
    get_mlst_allele_matches
)
from api.validators import validate_list_of_ids
from mlst.models import MLST
from cgmlst.models import CGMLST

from api.utils import timeit


class MLSTViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = MLST.objects.all()
    serializer_class = MLSTSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of sample IDs, return MLST results."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })

            result, qt = timeit(
                get_sequence_type,
                request.data['ids'],
                request.user
            )
            return self.formatted_response(result, query_time=qt)

    @list_route(methods=['post'])
    def blast_by_sample(self, request):
        """Given a list of sample IDs, return BLAST results."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })

            result, qt = timeit(
                get_mlst_blast_results,
                request.data['ids'],
                request.user
            )
            return self.formatted_response(result, query_time=qt)

    @list_route(methods=['post'])
    def allele_by_sample(self, request):
        """Given a list of sample IDs, return number alleles with match."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })

            result, qt = timeit(
                get_mlst_allele_matches,
                request.data['ids'],
                request.user
            )
            return self.formatted_response(result, query_time=qt)


class CGMLSTViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = CGMLST.objects.all()
    serializer_class = CGMLSTSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of sample IDs, return SRST2 results."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })

            result, qt = timeit(
                get_cgmlst,
                request.data['ids'],
                request.user
            )
            return self.formatted_response(result, query_time=qt)
