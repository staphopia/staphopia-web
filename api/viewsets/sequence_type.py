from django.db import connection

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.serializers import SequenceTypeSerializer
from mlst.models import Srst2


class MLSTViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """

    def list(self, request):
        cursor = connection.cursor()
        q = "SELECT * FROM top_sequence_types(1000000)"
        cursor.execute(q)

        result = []
        base_url = request.build_absolute_uri()
        for row in cursor.fetchall():

            result.append({
                'st': row[0],
                'count': row[1],
                'url': '{0}{1}/'.format(base_url, row[0])
            })

        return Response(result)

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        """
        Stored metadata information for a given sample.
        """
        queryset = Srst2.objects.filter(st_stripped=pk).prefetch_related("sample")
        serializer = SequenceTypeSerializer(queryset, many=True)
        return Response(serializer.data)
