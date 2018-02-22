from rest_framework.decorators import list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.queries.genes import (
    get_gene_features_by_product,
    get_genes_by_sample,
    get_gene_feature,
    get_gene_features,
    get_clusters_by_samples,
    get_cluster_counts_by_samples
)
from api.validators import validate_positive_integer, validate_list_of_ids
from api.serializers.annotations import (
    AnnotationSerializer,
    AnnotationRepeatSerializer,
    AnnotationFeatureSerializer,
    AnnotationInferenceSerializer
)
from annotation.models import (
    Annotation,
    Repeat,
    Feature,
    Inference
)
from api.utils import timeit


class AnnotationViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene features."""

    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def list(self, request):
        return Response({"message": "Please use bulk_by_sample"})

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
                product = False
                if 'product_id' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['product_id']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        product = request.GET['product_id']

                results, qt = timeit(
                    get_genes_by_sample,
                    request.data['ids'],
                    request.user.pk,
                    product_id=product
                )
                return self.formatted_response(results, query_time=qt)


class AnnotationFeatureViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene products."""

    queryset = Feature.objects.all()
    serializer_class = AnnotationFeatureSerializer

    def list(self, request):
        if 'term' in request.GET:
                queryset = Feature.objects.filter(
                    product__icontains=request.GET['term']
                )
        else:
            queryset = Feature.objects.all()

        return self.paginate(queryset, serializer=AnnotationFeatureSerializer,
                             page_size=100)


class AnnotationRepeatViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene inferences."""

    queryset = Repeat.objects.all()
    serializer_class = AnnotationRepeatSerializer


class AnnotationInferenceViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving gene inferences."""

    queryset = Inference.objects.all()
    serializer_class = AnnotationInferenceSerializer
