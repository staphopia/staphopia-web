from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.info import (
    get_sequencing_stats_by_year,
    get_assembly_stats_by_year
)


class StatusViewSet(CustomReadOnlyModelViewSet):
    """
    Provide a simple "database is working" status.
    """
    def list(self, request):
        """
        Determine if database is up.
        """
        from django.db import connections
        from django.db.utils import OperationalError
        db = connections['default']
        connected = True
        try:
            db.cursor()
        except OperationalError:
            connected = False

        if connected:
            return Response(
                {"status": 'OK'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"status": 'FAIL'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class InfoViewSet(CustomReadOnlyModelViewSet):
    """
    View summary statistics of samples within database.
    """

    queryset = ''

    def list(self, request):
        """
        Stored metadata information for a given sample.
        """
        base_url = request.build_absolute_uri()
        sequencing = '{0}sequencing_by_year/'.format(base_url)
        assembly = '{0}assembly_by_year/'.format(base_url)
        urls = {
            'Sequencing Stats By Year': sequencing,
            'Assembly Stats By Year': assembly
        }

        return Response(urls)

    @list_route(methods=['get'])
    def sequencing_by_year(self, request):
        """
        Sequencing stats based on year samples were first public.
        """
        if 'is_original' in request.GET:
            return self.formatted_response(
                get_sequencing_stats_by_year(is_original=True)
            )
        else:
            return self.formatted_response(
                get_sequencing_stats_by_year(is_original=False)
            )

    @list_route(methods=['get'])
    def assembly_by_year(self, request):
        """
        Assembly stats based on year samples were first public.
        """
        if 'is_scaffolds' in request.GET and 'is_plasmids' in request.GET:
            return self.formatted_response(get_assembly_stats_by_year(
                is_scaffolds=True, is_plasmids=True
            ))
        elif 'is_scaffolds' in request.GET:
            return self.formatted_response(get_assembly_stats_by_year(
                is_scaffolds=True, is_plasmids=False
            ))
        elif 'is_plasmids' in request.GET:
            return self.formatted_response(get_assembly_stats_by_year(
                is_scaffolds=False, is_plasmids=True
            ))
        else:
            return self.formatted_response(get_assembly_stats_by_year(
                is_scaffolds=False, is_plasmids=False
            ))
