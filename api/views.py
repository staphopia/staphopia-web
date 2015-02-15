from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import (
    SampleSerializer,
    VariantSerializer
)

from samples.models import Sample
from analysis.models import (
    Variant,
    VariantToSNP,
    VariantSNP
)


class VariantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


@api_view(['GET'])
def sample_list(request, sample_tag):
    """
    API endpoint that allows users to be viewed or edited.
    """
    try:
        sample = Sample.objects.get(sample_tag=sample_tag)
    except Sample.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SampleSerializer(sample)
        return Response(serializer.data)
