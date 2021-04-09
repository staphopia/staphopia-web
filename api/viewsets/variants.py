"""Viewsets related to Variant tables."""
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import format_results, get_ids_in_bulk
from api.queries.variants import (
    get_variant_counts,
    get_variant_count_by_position,
    get_samples_by_snp,
    get_samples_by_indel,
    get_indels_by_sample,
    get_snps_by_sample,
    get_variant_counts_by_samples,
    get_representative_sequence,
    get_variant_annotation
)
from api.validators import validate_positive_integer, validate_list_of_ids
from api.utils import timeit

from variant.models import (
    SNP,
    Indel,
    Annotation,
    Counts,
    Comment,
    Feature,
    Filter,
    Reference,
    Variant
)
from api.serializers.variants import (
    VariantSerializer,
    SNPSerializer,
    InDelSerializer,
    AnnotationSerializer,
    VariantCountsSerializer,
    CommentSerializer,
    FilterSerializer,
    FeatureSerializer,
    ReferenceSerializer
)


class VariantCountsViewSet(CustomReadOnlyModelViewSet):
    """Break down of variant counts by reference position."""
    queryset = Counts.objects.all()
    serializer_class = VariantCountsSerializer

    def retrieve(self, request, pk=None):
        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator)
        else:
            results, qt = timeit(
                get_variant_count_by_position,
                [pk]
            )
            return self.formatted_response(results, query_time=qt)

    def list(self, request):
        annotation_id = None
        if 'annotation_id' in request.GET:
            validator = validate_positive_integer(
                request.GET['annotation_id']
            )
            if validator['has_errors']:
                return Response(validator)
            else:
                annotation_id = request.GET['annotation_id']

        if annotation_id:
            results, qt = timeit(
                get_variant_count_by_position,
                [annotation_id],
                is_annotation=True
            )
            return self.formatted_response(results, query_time=qt)
        else:
            return self.paginate(Counts.objects.order_by('position'),
                                 serializer=VariantCountsSerializer,
                                 page_size=200)

    @list_route(methods=['post'])
    def bulk(self, request):
        """Given a list of reference positions, return variant counts."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })
            else:
                is_annotation = False
                if 'is_annotation' in request.GET:
                    is_annotation = True

                results, qt = timeit(
                    get_variant_count_by_position,
                    request.data['ids'],
                    is_annotation=is_annotation
                )
                return self.formatted_response(results, query_time=qt)

class VariantViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving variants."""
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

    def list(self, request):
        return Response({
            "message": "Please use indel_bulk_by_sample or snp_bulk_by_sample"
        })

    @list_route(methods=['post'])
    def snp_bulk_by_sample(self, request):
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

                temp_start = None
                if 'start' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['start']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        temp_start = request.GET['start']

                temp_end = None
                if 'end' in request.GET:
                    validator = validate_positive_integer(
                        request.GET['end']
                    )
                    if validator['has_errors']:
                        return Response(validator)
                    else:
                        temp_end = request.GET['end']

                start = None
                end = None
                if temp_start and temp_end:
                    start = min(temp_start, temp_end)
                    end = max(temp_start, temp_end)
                else:
                    # Incase only one was given
                    start = None
                    end = None

                return self.formatted_response(get_snps_by_sample(
                    request.data['ids'],
                    request.user.pk,
                    annotation_id=annotation_id,
                    start=start,
                    end=end
                ))

        results, qt = timeit(
            get_samples_by_snp,
            [pk],
            request.user.pk
        )
        return self.paginate(results, page_size=2000, is_serialized=True)

    @list_route(methods=['post'])
    def indel_bulk_by_sample(self, request):
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

    @list_route(methods=['post'])
    def counts_in_bulk(self, request):
        """Given a list of Sample IDs, return SNP and InDel counts for each."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                            "message": validator['message'],
                            "data": request.data
                        })

            return self.formatted_response(get_variant_counts(
                request.data['ids'],
                request.user.pk
            ))


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
        """Return list of samples associated with a given SNP id."""
        results, qt = timeit(
            get_samples_by_snp,
            [pk],
            request.user.pk
        )
        return self.paginate(results, page_size=2000, is_serialized=True)


    @list_route(methods=['post'])
    def bulk_samples(self, request):
        """Return list of samples associated with a given list of SNP ids."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=100)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                results, qt = timeit(
                    get_samples_by_snp,
                    request.data['ids'],
                    request.user.pk,
                    bulk=True
                )
                return self.formatted_response(results, query_time=qt)

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
        """Return list of samples associated with a given Indel id."""
        results, qt = timeit(
            get_samples_by_indel,
            [pk],
            request.user.pk
        )
        return self.paginate(results, page_size=2000, is_serialized=True)

    @list_route(methods=['post'])
    def bulk_samples(self, request):
        """Return list of samples associated with a given list of Indel ids."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=100)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                results, qt = timeit(
                    get_samples_by_indel,
                    request.data['ids'],
                    request.user.pk,
                    bulk=True
                )
                return self.formatted_response(results, query_time=qt)

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

class VariantAnnotationViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving SNP."""

    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def list(self, request):
        if 'locus_tag' in request.GET:
            queryset = get_variant_annotation(
                None, locus_tag=request.GET['locus_tag']
            )
        else:
            queryset = get_variant_annotation(None)

        return self.paginate(queryset, is_serialized=True, page_size=500)

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

            return self.formatted_response(get_variant_annotation(
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
                request.user.pk,
                annotation_ids
            )
            time = int((time.time() - start) * 1000.0)

            return self.formatted_response(results, query_time=time)


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
