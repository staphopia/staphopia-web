from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.sccmecs import (
    get_sccmec_primers_by_sample,
    get_sccmec_proteins_by_sample
)
from api.serializers.sccmecs import (
    SCCmecCassetteSerializer,
    SCCmecCoverageSerializer,
    SCCmecProteinSerializer
)
from api.validators import validate_list_of_ids

from sccmec.models import Cassette, Coverage, Proteins


class SCCmecCassetteViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec cassettes."""

    queryset = Cassette.objects.all()
    serializer_class = SCCmecCassetteSerializer


class SCCmecCoverageViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec cassette coverage."""

    queryset = Coverage.objects.all()
    serializer_class = SCCmecCoverageSerializer


class SCCmecPrimerViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec primer hits."""

    queryset = ''

    def list(self, request):
        """
        Stored SCCmec primer hit information for a given sample.
        """
        urls = {
            'msg': 'Must use bulk_by_sample to get SCCmec Primer hits',
        }

        return Response(urls)

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return SCCmec Primer for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                return self.formatted_response(get_sccmec_primers_by_sample(
                    request.data['ids'],
                    request.user.pk,
                    exact_hits=True if 'exact_hits' in request.GET else False,
                    predict=True if 'predict' in request.GET else False
                ))


class SCCmecProteinViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec protein hits."""

    queryset = Proteins.objects.all()
    serializer_class = SCCmecProteinSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return SCCmec protein hits."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                return self.formatted_response(get_sccmec_proteins_by_sample(
                    request.data['ids'],
                    request.user.pk
                ))


class SCCmecSubtypeViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec Subtype hits."""

    queryset = ''

    def list(self, request):
        """
        Stored SCCmec Subtype hit information for a given sample.
        """
        urls = {
            'msg': 'Must use bulk_by_sample to get SCCmec Subtype hits',
        }

        return Response(urls)

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return SCCmec subtype hits Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                return self.formatted_response(get_sccmec_primers_by_sample(
                    request.data['ids'],
                    request.user.pk,
                    is_subtypes=True,
                    exact_hits=True if 'exact_hits' in request.GET else False,
                    predict=True if 'predict' in request.GET else False
                ))
