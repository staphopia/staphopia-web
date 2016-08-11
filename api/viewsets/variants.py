"""Viewsets related to Variant tables."""
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import format_results, get_ids_in_bulk, get_snps_by_samples
from api.validators import validate_list_of_ids
from variant.models import (
    SNP,
    ToSNP,
    Indel,
    ToIndel,
    Annotation,
    Comment,
    Confidence,
    Feature,
    Filter,
    Reference
)
from api.serializers.variants import (
    SNPSerializer,
    InDelSerializer,
    AnnotationSerializer,
    CommentSerializer,
    ConfidenceSerializer,
    FilterSerializer,
    FeatureSerializer,
    ReferenceSerializer
)


class SNPViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = SNP.objects.all()
    serializer_class = SNPSerializer

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
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                return self.formatted_response(get_snps_by_samples(
                    request.data['ids'],
                ))


class InDelViewSet(viewsets.ReadOnlyModelViewSet):
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
                return Response(get_ids_in_bulk(
                    'variant_toindel',
                    request.data['ids'],
                    id_col='sample_id'
                ))


class AnnotationViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

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


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class ConfidenceViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Confidence.objects.all()
    serializer_class = ConfidenceSerializer

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
                    'variant_confidence',
                    request.data['ids']
                ))


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
