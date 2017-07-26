from rest_framework.response import Response

from rest_framework import mixins, status, viewsets

from api.utils import format_results


class CustomReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    def formatted_response(self, data, time=None, return_empty=False,
                           status=status.HTTP_200_OK, limit=None):
        if len(data) or return_empty:
            return Response(format_results(data, time=time, limit=limit), status=status)
        else:
            data = {
                "count": 0,
                "results": [],
                "message": "Query did not return any hits."
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def paginate(self, queryset, serializer=None, page_size=None,
                 is_serialized=False):
        if page_size:
            self.paginator.page_size = page_size

        page = self.paginate_queryset(queryset)
        if page is not None:
            if is_serialized:
                return self.get_paginated_response(page)
            else:
                serialized = serializer(page, many=True)
                return self.get_paginated_response(serialized.data)

        if is_serialized:
            return self.formatted_response(queryset)
        else:
            serializer = serializer(queryset, many=True)
            return self.formatted_response(serializer.data)

    pass
