from rest_framework.response import Response
from rest_framework.decorators import list_route

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.resistances import (
    get_ariba_resistance_report,
    get_ariba_resistance_summary,
    get_ariba_resistance
)
from api.serializers.resistances import ResistanceAribaSerializer
from api.validators import validate_list_of_ids
from api.utils import timeit

from resistance.models import Cluster, ResistanceClass, Ariba, AribaSequence


class ResistanceAribaViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ariba resistance."""

    queryset = Ariba.objects.all()
    serializer_class = ResistanceAribaSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return resistance info for each."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                if 'summary' in request.GET:
                    result, qt = timeit(
                        get_ariba_resistance_summary,
                        request.data['ids'],
                        request.user.pk
                    )
                elif 'report' in request.GET:
                    result, qt = timeit(
                        get_ariba_resistance_report,
                        request.data['ids'],
                        request.user.pk
                    )
                else:
                    result, qt = timeit(
                        get_ariba_resistance,
                        request.data['ids'],
                        request.user.pk
                    )
                return self.formatted_response(result, query_time=qt)
