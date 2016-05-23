from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.utils import format_results
from api.serializers.genes import (
    GeneClusterSerializer,
    GeneFeatureSerializer,
    GeneProductSerializer,
    GeneInferenceSerializer,
    GeneNoteSerializer,
    GeneBlastSerializer
)
from gene.models import (
    Clusters,
    Features,
    Product,
    Inference,
    Note,
    BlastResults
)


class GeneClusterViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene clusters."""

    queryset = Clusters.objects.all()
    serializer_class = GeneClusterSerializer

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        """Return a list of samples with a given snp."""
        hits = Features.objects.filter(cluster_id=pk).values_list(
            'sample_id', flat=True
        )
        return Response(format_results(hits))


class GeneFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene features."""

    queryset = Features.objects.all()
    serializer_class = GeneFeatureSerializer


class GeneProductViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene products."""

    queryset = Product.objects.all()
    serializer_class = GeneProductSerializer


class GeneInferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene inferences."""

    queryset = Inference.objects.all()
    serializer_class = GeneInferenceSerializer


class GeneNoteViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene notes."""

    queryset = Note.objects.all()
    serializer_class = GeneNoteSerializer


class GeneBlastViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene blast hits."""

    queryset = BlastResults.objects.all()
    serializer_class = GeneBlastSerializer
