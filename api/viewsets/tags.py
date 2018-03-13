from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.tags import TagSerializer
from api.queries.tags import (
    get_samples_by_tag,
    get_all_tags,
    get_user_tags,
    get_public_tags
)

from api.utils import timeit
from api.validators import validate_positive_integer, validate_list_of_ids

from tag.models import Tag


class TagViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request):
        tags = None
        tag = None
        if 'tag' in request.GET:
            tag = request.GET['tag']

        if 'public' in request.GET:
            tags = get_public_tags(tag=tag)
        elif 'user' in request.GET:
            tags = get_user_tags(request.user.pk, tag=tag)
        else:
            tags = get_all_tags(tag=tag)

        return self.paginate(tags, page_size=500, is_serialized=True)

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        result, qt = timeit(get_samples_by_tag, pk)
        return self.formatted_response(result, query_time=qt)
