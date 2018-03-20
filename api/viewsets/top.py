from django.db import connection

from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import query_database

class TopViewSet(CustomReadOnlyModelViewSet):
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
        sql = """SELECT sequencing_center, count
                 FROM top_sequencing_centers({0})""".format(total)

        return self.formatted_response(query_database(sql))

    @detail_route(methods=['get'])
    def sequence_types(self, request, pk=10):
        """
        Stored metadata information for a given sample.
        """
        sql = """SELECT sequence_type as st, count
                 FROM top_sequence_types()"""
        results = []
        total = 0
        for row in query_database(sql):
            results.append({
                'st': row['st'],
                'count': row['count']
            })
            total += row['count']

        output = []
        current = 0
        total_percent = 0
        for result in results:
            if current == int(pk):
                break
            current += 1
            percent = result["count"] / total * 100
            total_percent += percent
            output.append({
                'st': result['st'],
                'count': result['count'],
                'percent': float(f'{percent:2.2f}'),
                'overall': float(f'{total_percent:2.2f}')
            })

        return self.formatted_response(output)
