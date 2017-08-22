from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.search import basic_search

class SearchViewSet(CustomReadOnlyModelViewSet):
    """Search function viewset."""

    queryset = ''

    def list(self, request):
        if 'q' in request.GET:
            queryset = basic_search(request.GET['q'])
        else:
            queryset = basic_search("", all_samples=True)

        return self.paginate(queryset, is_serialized=True)
