from rest_framework import viewsets

from api.serializers.sccmecs import (
    SCCmecCassetteSerializer,
    SCCmecCoverageSerializer,
    SCCmecPrimerSerializer,
    SCCmecProteinSerializer
)
from sccmec.models import Cassette, Coverage, Primers, Proteins


class SCCmecCassetteViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec cassettes."""

    queryset = Cassette.objects.all()
    serializer_class = SCCmecCassetteSerializer


class SCCmecCoverageViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec cassette coverage."""

    queryset = Coverage.objects.all()
    serializer_class = SCCmecCoverageSerializer


class SCCmecPrimerViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec primer hits."""

    queryset = Primers.objects.all()
    serializer_class = SCCmecPrimerSerializer


class SCCmecProteinViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SCCmec protein hits."""

    queryset = Proteins.objects.all()
    serializer_class = SCCmecProteinSerializer
