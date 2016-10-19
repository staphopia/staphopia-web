from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import get_gene_features_by_product, format_results
from api.validators import validate_positive_integer
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


class GeneFeatureViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene features."""

    queryset = Features.objects.all()
    serializer_class = GeneFeatureSerializer

    def list(self, request):
        if 'product_id' in request.GET:
            validator = validate_positive_integer(request.GET['product_id'])
            if validator['has_errors']:
                return Response(validator)
            else:
                queryset = Features.objects.filter(
                    product_id=request.GET['product_id']
                )
        else:
            queryset = Features.objects.all()

        return self.paginate(queryset, serializer=GeneFeatureSerializer,
                             page_size=10)


class GeneProductViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene products."""

    queryset = Product.objects.all()
    serializer_class = GeneProductSerializer

    @detail_route(methods=['get'])
    def genes(self, request, pk=None):
        """Return a list of genes with a given snp."""
        return self.paginate(get_gene_features_by_product(pk), page_size=100,
                             is_serialized=True)

    def list(self, request):
        if 'term' in request.GET:
                queryset = Product.objects.filter(
                    product__icontains=request.GET['term']
                )
        else:
            queryset = Product.objects.all()

        return self.paginate(queryset, serializer=GeneProductSerializer,
                             page_size=100)


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
