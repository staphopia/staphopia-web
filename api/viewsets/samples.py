from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.serializers import SampleSerializer, MetaDataSerializer
from sample.models import MetaData


class SampleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    serializer_class = SampleSerializer
    queryset = MetaData.objects.all()

    @detail_route(methods=['get'])
    def metadata(self, request, pk=None):
        """
        Stored metadata information for a given sample.
        """
        sample = MetaData.objects.get(sample_tag=pk)
        serializer = MetaDataSerializer(sample)
        return Response(serializer.data)
