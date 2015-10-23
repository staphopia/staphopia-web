from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.serializers import SampleSerializer


from sample.models import MetaData


@api_view(['GET'])
def sample_list(request):
    """
    API endpoint that allows users to be viewed or edited.
    """
    try:
        samples = MetaData.objects.all()
        paginator = PageNumberPagination()
        subset = paginator.paginate_queryset(samples, request)
    except MetaData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SampleSerializer(
            subset, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def sample_info(request, sample_tag):
    """
    API endpoint that allows users to be viewed or edited.
    """
    try:
        sample = MetaData.objects.get(sample_tag=sample_tag)
    except MetaData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SampleSerializer(sample, context={'request': request})
        return Response(serializer.data)
