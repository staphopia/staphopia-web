from collections import OrderedDict

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
                'get_samples': '{0}{1}/samples/'.format(base_url, row[0]),
                'get_sccmec_status': '{0}{1}/sccmec/'.format(base_url, row[0])
            })

        return Response(result)

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        """
        Stored metadata information for a given sample.
        """
        q = Srst2.objects.filter(st_stripped=pk).prefetch_related("sample")
        serializer = SequenceTypeSerializer(
            q, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def sccmec(self, request, pk=None):
        """
        Stored metadata information for a given sample.
        """
        sequence_type = pk
        cutoff = request.GET['cutoff'] if 'cutoff' in request.GET else 0.70
        try:
            cutoff = float(cutoff)
        except ValueError:
            cutoff = 0.70

        only_positive = True if 'only_positive' in request.GET else False

        cursor = connection.cursor()
        q = "SELECT * FROM sccmec_status_by_st({0})".format(sequence_type)
        cursor.execute(q)

        results = []
        exact_matches = 0
        for row in cursor.fetchall():
            status = 'positive' if row[2] >= cutoff else 'negative'
            if only_positive and status is 'negative':
                continue

            if row[3]:
                exact_matches += 1

            results.append({
                'sample_tag': row[0],
                'st': row[1],
                'sccmec_status': status,
                'mecA_coverage': row[2],
                'st_is_exact_match': row[3]
            })

        data = OrderedDict((
            ('total', len(results)),
            ('exact_st_matches', exact_matches),
            ('results', results)
        ))

        return Response(data)
