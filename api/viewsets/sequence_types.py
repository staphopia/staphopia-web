from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.serializers.sequence_types import BlastSerializer, Srst2Serializer
from mlst.models import Srst2, Blast


class MlstBlastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Blast.objects.all()
    serializer_class = BlastSerializer


class MlstSrst2ViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Srst2.objects.all()
    serializer_class = Srst2Serializer
