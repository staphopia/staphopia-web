"""Viewsets related to Kmer tables."""
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import get_kmer_by_string
from kmer.models import Total
from api.serializers.kmers import KmerTotalSerializer


class KmerViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Total.objects.all()
    serializer_class = KmerTotalSerializer

    def retrieve(self, request, pk=None):
        """Query kmer against Elastic Search cluster."""
        return Response(get_kmer_by_string(pk.upper()))
