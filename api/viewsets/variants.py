"""Viewsets related to Variant tables."""
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import format_results, get_ids_in_bulk
from api.queries.variants import (
    get_indels_by_sample,
    get_snps_by_sample,
    get_variant_counts_by_samples,
    get_representative_sequence
)
from api.validators import validate_positive_integer, validate_list_of_ids

from variant.models import (
    SNP,
    ToSNP,
    Indel,
    ToIndel,
    Annotation,
    Comment,
    Feature,
    Filter,
    Reference,
    Counts
)
from api.serializers.variants import (
    SNPSerializer,
    InDelSerializer,
    AnnotationSerializer,
    CommentSerializer,
    FilterSerializer,
    FeatureSerializer,
    ReferenceSerializer,
    CountsSerializer
)


class SNPViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = SNP.objects.all()
    serializer_class = SNPSerializer

    def list(self, request):
        if 'reference_position' in request.GET:
            validator = validate_positive_integer(
                request.GET['reference_position']
            )
            if validator['has_errors']:
                return Response(validator)
            else:
                queryset = SNP.objects.filter(
                    reference_position=request.GET['reference_position']
                )
        else:
            queryset = SNP.objects.all()

        return self.paginate(queryset, serializer=SNPSerializer)

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        """Return a list of samples with a given snp."""
        hits = ToSNP.objects.filter(snp_id=pk).values_list(
            'sample_id', flat=True
        )
        return Response(format_results(hits))

    @list_route(methods=['post'])
    def bulk(self, request):
        """Given a list of SNP IDs, return table info for each SNP."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=10000)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                return self.formatted_response(get_ids_in_bulk(
                    'variant_snp',
                    request.data['ids']
                ))

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of SNP IDs, return table info for each SNP."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=10)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                annotation_id = None
                if 'annotation_id' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['annotation_id']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        annotation_id = request.GET['annotation_id']

                return self.formatted_response(get_snps_by_sample(
                    request.data['ids'],
                    request.user.pk,
                    annotation_id=annotation_id
                ))


class InDelViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving InDel."""

    queryset = Indel.objects.all()
    serializer_class = InDelSerializer

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        """Return a list of samples with a given snp."""
        hits = ToIndel.objects.filter(indel_id=pk).values_list(
            'sample_id', flat=True
        )
        return Response(format_results(hits))

    @list_route(methods=['post'])
    def bulk(self, request):
        """Given a list of InDel IDs, return table info for each InDel."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                return Response(get_ids_in_bulk(
                    'variant_indel',
                    request.data['ids']
                ))

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of InDel IDs, return table info for each InDel."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                annotation_id = None
                if 'annotation_id' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['annotation_id']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        annotation_id = request.GET['annotation_id']

                return self.formatted_response(get_indels_by_sample(
                    request.data['ids'],
                    request.user.pk,
                    annotation_id=annotation_id
                ))


class AnnotationViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def list(self, request):
        if 'locus_tag' in request.GET:
            queryset = Annotation.objects.filter(
                locus_tag=request.GET['locus_tag']
            )
        else:
            queryset = Annotation.objects.all()

        return self.paginate(queryset, serializer=AnnotationSerializer)

    @list_route(methods=['post'])
    def bulk(self, request):
        """Given a list of Annotation IDs, return info for each Annotation."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                return Response(get_ids_in_bulk(
                    'variant_annotation',
                    request.data['ids']
                ))

    @list_route(methods=['post'])
    def generate_variant_sequence(self, request):
        """Return a list of samples with a given snp."""
        import time
        start = time.time()
        if request.method == 'POST':
            sample_ids = request.data['ids']
            annotation_ids = request.data['extra']['annotation_ids']
            validator = validate_list_of_ids(request.data)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            elif validator['make_list']:
                sample_ids = [sample_ids]

            validator = validate_list_of_ids(request.data['extra'],
                                             field='annotation_ids')
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            elif validator['make_list']:
                annotation_ids = [annotation_ids]

            results = get_representative_sequence(
                sample_ids,
                annotation_ids,
                save_reference=request.data['extra']['save_reference']
            )
            time = '{0}ms'.format(int((time.time() - start) * 1000.0))

            return self.formatted_response(results, time=time)


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer


class FilterViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Filter.objects.all()
    serializer_class = FilterSerializer


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class CountsViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving Variant Counts."""

    queryset = Counts.objects.all()
    serializer_class = CountsSerializer

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return SNP and InDel Counts."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                return self.formatted_response(get_variant_counts_by_samples(
                    request.data['ids'],
                ))
