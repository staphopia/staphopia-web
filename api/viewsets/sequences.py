from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.sequences import SequenceStatSerializer
from api.queries.sequences import get_sequencing_stats
from api.validators import validate_list_of_ids

from sequence.models import Summary


class SequenceStatViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Summary.objects.all()
    serializer_class = SequenceStatSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, get Sequencine info for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                is_original = 'TRUE' if 'original' in request.GET else 'FALSE'
                qual_per_base = True if 'bases' in request.GET else False
                read_lengths = True if 'lengths' in request.GET else False
                return self.formatted_response(get_sequencing_stats(
                    request.data['ids'],
                    request.user.pk,
                    is_original=is_original,
                    qual_per_base=qual_per_base,
                    read_lengths=read_lengths
                ))
