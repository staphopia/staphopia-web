from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import (
    get_gene_features_by_product,
    get_genes_by_samples,
    get_gene_feature,
    get_gene_features,
    format_results,
    get_clusters_by_samples,
    get_cluster_counts_by_samples
)
from api.validators import validate_positive_integer, validate_list_of_ids
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


class GeneClusterViewSet(CustomReadOnlyModelViewSet):
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

    @list_route(methods=['post'])
    def clusters_by_samples(self, request):
        """Given a list of sample IDs, return table info for each gene."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                return self.formatted_response(
                        get_clusters_by_samples(request.data['ids']))

    @list_route(methods=['post'])
    def cluster_counts_by_samples(self, request):
        """Given a list of sample IDs, return table info for each gene."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=50000)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                return self.formatted_response(
                        get_cluster_counts_by_samples(request.data['ids']))


class GeneFeatureViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene features."""

    queryset = Features.objects.all()
    serializer_class = GeneFeatureSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of sample IDs, return table info for each gene."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                if 'product_id' in request.GET and 'cluster_id' in request.GET:
                    product = validate_positive_integer(
                        request.GET['product_id']
                    )
                    cluster = validate_positive_integer(
                        request.GET['cluster_id']
                    )
                    if product['has_errors']:
                        return Response(product)
                    elif cluster['has_errors']:
                        return Response(cluster)
                    else:
                        return self.paginate(
                            get_genes_by_samples(
                                request.data['ids'],
                                product_id=request.GET['product_id'],
                                cluster_id=request.GET['cluster_id']
                            ),
                            page_size=100, is_serialized=True
                        )
                elif 'product_id' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['product_id']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        return self.paginate(
                            get_genes_by_samples(
                                request.data['ids'],
                                product_id=request.GET['product_id']
                            ),
                            page_size=100, is_serialized=True
                        )
                elif 'cluster_id' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['cluster_id']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        return self.paginate(
                            get_genes_by_samples(
                                request.data['ids'],
                                cluster_id=request.GET['cluster_id']
                            ),
                            page_size=100, is_serialized=True
                        )
                else:
                    return self.paginate(
                        get_genes_by_samples(request.data['ids']),
                        page_size=100, is_serialized=True
                    )

    def retrieve(self, request, pk=None):
        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator)
        else:
            return self.paginate(get_gene_feature(pk), is_serialized=True)

    def list(self, request):
        """Adjust the default listing of genes."""
        queryset = None
        if 'product_id' in request.GET and 'cluster_id' in request.GET:
            product = validate_positive_integer(request.GET['product_id'])
            cluster = validate_positive_integer(request.GET['cluster_id'])
            if product['has_errors']:
                return Response(product)
            elif cluster['has_errors']:
                return Response(cluster)
            else:
                queryset = get_gene_features(
                    product_id=request.GET['product_id'],
                    cluster_id=request.GET['cluster_id']
                )
        elif 'product_id' in request.GET:
            validator = validate_positive_integer(request.GET['product_id'])
            if validator['has_errors']:
                return Response(validator)
            else:
                queryset = get_gene_features(
                    product_id=request.GET['product_id']
                )
        elif 'cluster_id' in request.GET:
            validator = validate_positive_integer(request.GET['cluster_id'])
            if validator['has_errors']:
                return Response(validator)
            else:
                queryset = get_gene_features(
                    cluster_id=request.GET['cluster_id']
                )
        else:
            return Response({
                "message": ("Unable to retrieve all gene features, you must "
                            "use filters such as 'product_id' and "
                            "'cluster_id'.")
            })

        return self.paginate(queryset, is_serialized=True, page_size=100)


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
