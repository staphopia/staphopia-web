from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.info import (
    get_sequencing_stats_by_year,
    get_submission_by_year,
    get_assembly_stats_by_year,
    get_rank_by_year,
    get_st_by_year,
    get_cgmlst_patterns,
    get_publication_links
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

        urls = {
            'Sequencing Stats By Year': f'{base_url}sequencing_by_year/',
            'Assembly Stats By Year': f'{base_url}assembly_by_year/',
            'Public Submissions By Year': f'{base_url}submission_by_year/',
            'Publications By Year': f'{base_url}published_by_year/',
            'Rank By Year': f'{base_url}rank_by_year/',
            'ST By Year': f'{base_url}st_by_year/',
            'Public cgMLST Pattern Counts':  f'{base_url}cgmlst_patterns/',
            'Publication Links': f'{base_url}publication_links/'
        }

        return Response(urls)

    @list_route(methods=['get'])
    def st_by_year(self, request):
        """
        Sequencing type based on year samples were first public.
        """
        return self.formatted_response(
            get_st_by_year()
        )

    @list_route(methods=['get'])
    def cgmlst_patterns(self, request):
        """
        Public cgMLST pattern counts.
        """
        return self.formatted_response(
            get_cgmlst_patterns()
        )

    @list_route(methods=['get'])
    def publication_links(self, request):
        """
        How public sample publication links were made.
        """
        return self.formatted_response(
            get_publication_links()
        )

    @list_route(methods=['get'])
    def rank_by_year(self, request):
        """
        Sequencing rank based on year samples were first public.
        """
        if 'is_original' in request.GET:
            return self.formatted_response(
                get_rank_by_year(is_original=True)
            )
        else:
            return self.formatted_response(
                get_rank_by_year(is_original=False)
            )

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
    def submission_by_year(self, request):
        """
        Submission counts based on year samples were first public.
        """
        all_submissions = False
        if 'all' in request.GET:
            all_submissions = True

        return self.formatted_response(
            get_submission_by_year(all_submissions=all_submissions)
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
