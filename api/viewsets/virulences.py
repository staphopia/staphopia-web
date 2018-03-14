from rest_framework.response import Response
from rest_framework.decorators import list_route

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.virulences import get_ariba_virulence
from api.serializers.virulences import VirulenceAribaSerializer
from api.validators import validate_list_of_ids
from api.utils import timeit

from virulence.models import Cluster, Ariba, AribaSequence


class VirulenceAribaViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving ariba resistance."""

    queryset = Ariba.objects.all()
    serializer_class = VirulenceAribaSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return virulence info for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                result, qt = timeit(
                    get_ariba_virulence,
                    request.data['ids'],
                    request.user.pk
                )
                return self.formatted_response(result, query_time=qt)
