from django.db import connection

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response


class TopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View top X sequencing centers and sequence types. To see more (or less)
    than 10 change the number between top/XXX/sequencing_center/. For example
    to see  top 20 sequence types use top/20/sequence_types/
    """

    queryset = ''

    def list(self, request):
        """
        Stored metadata information for a given sample.
        """
        base_url = request.build_absolute_uri()
        seq_centers = '{0}10/sequencing_centers/'.format(base_url)
        seq_types = '{0}10/sequence_types/'.format(base_url)
        urls = {
            'Top 10 Sequencing Centers': seq_centers,
            'Top 10 Sequence Types': seq_types
        }

        return Response(urls)

    @detail_route(methods=['get'])
    def sequencing_centers(self, request, pk=10):
        """
        Stored metadata information for a given sample.
        """
        total = pk
        cursor = connection.cursor()
        q = """SELECT sequencing_center, count
               FROM top_sequencing_centers({0})""".format(total)
        cursor.execute(q)

        desc = cursor.description
        result = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        return Response(result)

    @detail_route(methods=['get'])
    def sequence_types(self, request, pk=10):
        """
        Stored metadata information for a given sample.
        """
        total = pk
        cursor = connection.cursor()
        q = """SELECT sequence_type, count
               FROM top_sequence_types({0})""".format(total)
        cursor.execute(q)

        desc = cursor.description
        result = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        return Response(result)
