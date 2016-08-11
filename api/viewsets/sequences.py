from rest_framework import viewsets

from api.serializers.sequences import SequenceStatSerializer
from sequence.models import Stat


class SequenceStatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Stat.objects.all()
    serializer_class = SequenceStatSerializer
