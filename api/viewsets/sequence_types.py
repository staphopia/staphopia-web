from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.sequence_types import MLSTSerializer
from api.queries.sequence_types import get_sequence_type
from api.validators import validate_list_of_ids
from mlst.models import MLST

from api.utils import timeit


class MLSTViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = MLST.objects.all()
    serializer_class = MLSTSerializer

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
                get_sequence_type,
                request.data['ids'],
                request.user.pk
            )
            return self.formatted_response(result, query_time=qt)
