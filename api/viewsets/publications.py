from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.publications import PublicationSerializer
from api.queries.publications import get_pmids, get_publications

from api.utils import timeit
from api.validators import validate_positive_integer, validate_list_of_ids

from publication.models import Publication


class PublicationViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

    def retrieve(self, request, pk=None):
        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator)
        else:
            results, qt = timeit(
                get_publications,
                [pk]
            )
            return self.formatted_response(results, query_time=qt)

    def list(self, request):
        pubs = None
        if 'pmid' in request.GET:
            validator = validate_positive_integer(request.GET['pmid'])
            if validator['has_errors']:
                return Response(validator)
            else:
                pubs = get_publications([request.GET['pmid']])
        else:
            pubs = get_publications(None)

        return self.paginate(pubs, page_size=500, is_serialized=True)

    @list_route(methods=['post'])
    def bulk(self, request):
        """Given a list of PubMed IDs, return publication information."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=100)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                results, qt = timeit(
                    get_publications,
                    request.data['ids']
                )
                return self.formatted_response(results, query_time=qt)

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return PMIDs."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                results, qt = timeit(
                    get_pmids,
                    request.data['ids'],
                    request.user.pk
                )
                return self.formatted_response(results, query_time=qt)
