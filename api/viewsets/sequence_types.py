from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.sequence_types import BlastSerializer, Srst2Serializer
from api.queries.sequence_types import (
    get_blast_sequence_type,
    get_srst2_sequence_type
)
from api.validators import validate_list_of_ids

from mlst.models import Srst2, Blast


class MlstBlastViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Blast.objects.all()
    serializer_class = BlastSerializer

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
            else:
                return self.formatted_response(get_blast_sequence_type(
                    request.data['ids'], request.user.pk
                ))


class MlstSrst2ViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Srst2.objects.all()
    serializer_class = Srst2Serializer

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
            else:
                return self.formatted_response(get_srst2_sequence_type(
                    request.data['ids'], request.user.pk
                ))
