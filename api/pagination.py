from collections import OrderedDict
import time

from rest_framework.response import Response
from rest_framework import mixins, status as rf_status, viewsets

from api.utils import format_results


class CustomReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """

    def formatted_response(self, data, query_time=None, return_empty=False,
                           status=rf_status.HTTP_200_OK, limit=None):
        if len(data) or return_empty:
            return Response(
                format_results(data, query_time=query_time, limit=limit),
                status=status
            )
        else:
            return Response(
                OrderedDict((
                    ("message", "Query did not return any hits."),
                    ("count", 0),
                    ("results", [])
                )),
                status=rf_status.HTTP_200_OK
            )

    def paginate(self, queryset, serializer=None, page_size=None,
                 is_serialized=False, query_time=None):
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
            return self.formatted_response(queryset,
                                           query_time=query_time)
        else:
            serializer = serializer(queryset, many=True)
            return self.formatted_response(serializer.data,
                                           query_time=query_time)
