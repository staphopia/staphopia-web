import time

from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.samples import SampleSerializer, MetadataSerializer

from api.queries.assemblies import get_assembly_stats, get_assembly_contigs
from api.queries.samples import (
    get_resistance_by_samples,
    get_samples,
    get_public_samples,
    get_sample_metadata
)

from api.queries.tags import get_tags_by_sample
from api.queries.genes import get_genes_by_sample
from api.queries.resistances import (
    get_ariba_resistance_report,
    get_ariba_resistance_summary,
    get_ariba_resistance
)

from api.queries.sequences import get_sequencing_stats
from api.queries.sequence_types import (
    get_unique_st_samples,
    get_mlst_blast_results,
    get_mlst_allele_matches,
    get_sequence_type,
    get_cgmlst
)

from api.queries.sccmecs import (
    get_sccmec_primers_by_sample,
    get_sccmec_coverage_by_sample,
    get_sccmec_proteins_by_sample
)
from api.queries.variants import (
    get_indels_by_sample,
    get_snps_by_sample,
    get_variant_counts
)
from api.queries.virulences import get_ariba_virulence
from api.utils import timeit
from api.validators import validate_positive_integer, validate_list_of_ids

from sample.models import Sample, Metadata


class SampleViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer

    def retrieve(self, request, pk=None):
        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator)
        else:
            return self.paginate(
                get_samples(request.user.pk, sample_id=pk), is_serialized=True
            )

    def list(self, request):
        st_filter = None
        if 'st' in request.GET:
            validator = validate_positive_integer(request.GET['st'])
            if validator['has_errors']:
                return Response(validator)
            else:
                st_filter = request.GET['st']

        if 'user_only' in request.GET:
            queryset = get_samples(request.user.pk, user_only=True,
                                   st=st_filter)
        elif 'name' in request.GET:
            queryset = get_samples(request.user.pk, name=request.GET['name'])
        else:
            queryset = get_samples(request.user.pk, st=st_filter)
        return self.paginate(queryset, is_serialized=True)

    @list_route(methods=['post'])
    def bulk(self, request):
        """Given a list of Sample IDs, return information for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=1000)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })

            results = get_samples(request.user.pk,
                                  sample_ids=request.data['ids'])
            return self.formatted_response(results)

    @list_route(methods=['get'])
    def public(self, request):
        """Return all public ENA samples."""
        samples = None
        limit = None
        if 'limit' in request.GET:
            validator = validate_positive_integer(request.GET['limit'])
            if validator['has_errors']:
                return Response(validator)
            else:
                limit = request.GET['limit']

        if 'include_location' in request.GET:
            samples = get_public_samples(include_location=True, limit=limit)
        else:
            samples = get_public_samples(limit=limit)
        return self.paginate(samples, page_size=500, is_serialized=True)

    @list_route(methods=['get'])
    def published(self, request):
        """Return all published ENA samples."""
        limit = None
        if 'limit' in request.GET:
            validator = validate_positive_integer(request.GET['limit'])
            if validator['has_errors']:
                return Response(validator)
            else:
                limit = request.GET['limit']

        samples = get_public_samples(is_published=True, limit=limit)
        return self.paginate(samples, page_size=500, is_serialized=True)

    @list_route(methods=['get'])
    def unique_st(self, request):
        """Return all public ENA samples with a unique ST."""
        samples = get_unique_st_samples()
        return self.paginate(samples, page_size=500, is_serialized=True)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        results, qt = timeit(get_tags_by_sample, pk, request.user.pk)
        return self.formatted_response(results, query_time=qt)

    @detail_route(methods=['get'])
    def assembly(self, request, pk=None):
        results, qt = timeit(
            get_assembly_stats,
            [pk],
            request.user.pk,
            is_plasmids=True if 'plasmids' in request.GET else False
        )
        return self.formatted_response(results, query_time=qt)

    @detail_route(methods=['get'])
    def plasmid(self, request, pk=None):
        results, qt = timeit(
            get_assembly_stats,
            [pk],
            request.user.pk,
            is_plasmids=True
        )
        return self.formatted_response(results, query_time=qt)

    @detail_route(methods=['get'])
    def contigs(self, request, pk=None):
        results, qt = timeit(
            get_assembly_contigs,
            [pk],
            request.user.pk,
            is_plasmids=True if 'plasmids' in request.GET else False
        )
        return self.paginate(results, page_size=30, is_serialized=True,
                             query_time=qt)

    @detail_route(methods=['get'])
    def genes(self, request, pk=None):
        product = None
        if 'product_id' in request.GET:
            product = validate_positive_integer(request.GET['product_id'])
            if product['has_errors']:
                return Response(product)
            else:
                product = request.GET['product_id']

        results, qt = timeit(
            get_genes_by_sample,
            [pk],
            request.user.pk,
            product_id=product,
        )
        return self.paginate(results, page_size=250, is_serialized=True,
                             query_time=qt)

    @detail_route(methods=['get'])
    def indels(self, request, pk=None):
        annotation_id = None
        if 'annotation_id' in request.GET:
            validator = validate_positive_integer(
                request.GET['annotation_id']
            )
            if validator['has_errors']:
                return Response(validator)
            else:
                annotation_id = request.GET['annotation_id']

        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if 'paginate' in request.GET:
                return self.paginate(
                    get_indels_by_sample([pk], request.user.pk,
                                         annotation_id=annotation_id),
                    page_size=100,
                    is_serialized=True
                )
            else:
                results, qt = timeit(
                    get_indels_by_sample,
                    [pk],
                    request.user.pk,
                    annotation_id=annotation_id
                )
                return self.formatted_response(results, query_time=qt)

    @detail_route(methods=['get'])
    def metadata(self, request, pk=None):
        result, qt = timeit(get_sample_metadata, [pk],  request.user.pk)
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def qc(self, request, pk=None):
        result, qt = timeit(
            get_sequencing_stats,
            [pk],
            request.user.pk,
            stage=request.GET['stage'] if 'stage' in request.GET else False,
            qual_per_base=True if 'bases' in request.GET else False,
            read_lengths=True if 'lengths' in request.GET else False
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def resistance(self, request, pk=None):
        if 'summary' in request.GET:
            result, qt = timeit(
                get_ariba_resistance_summary,
                [pk],
                request.user.pk
            )
        elif 'report' in request.GET:
            result, qt = timeit(
                get_ariba_resistance_report,
                [pk],
                request.user.pk
            )
        else:
            result, qt = timeit(
                get_ariba_resistance,
                [pk],
                request.user.pk
            )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def sccmec_coverages(self, request, pk=None):
        result, qt = timeit(
            get_sccmec_coverage_by_sample,
            [pk],
            request.user.pk
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def sccmec_primers(self, request, pk=None):
        result, qt = timeit(
            get_sccmec_primers_by_sample,
            [pk],
            request.user.pk,
            exact_hits=True if 'exact_hits' in request.GET else False,
            predict=True if 'predict' in request.GET else False
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def sccmec_subtypes(self, request, pk=None):
        result, qt = timeit(
            get_sccmec_primers_by_sample,
            [pk],
            request.user.pk,
            is_subtypes=True,
            exact_hits=True if 'exact_hits' in request.GET else False,
            predict=True if 'predict' in request.GET else False
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def sccmec_proteins(self, request, pk=None):
        result, qt = timeit(
            get_sccmec_proteins_by_sample,
            [pk],
            request.user.pk
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def snps(self, request, pk=None):
        annotation_id = None
        if 'annotation_id' in request.GET:
            validator = validate_positive_integer(
                request.GET['annotation_id']
            )
            if validator['has_errors']:
                return Response(validator)
            else:
                annotation_id = request.GET['annotation_id']

        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if 'paginate' in request.GET:
                return self.paginate(
                    get_snps_by_sample([pk], request.user.pk,
                                       annotation_id=annotation_id),
                    page_size=100,
                    is_serialized=True
                )
            else:
                result, qt = timeit(
                    get_snps_by_sample,
                    [pk],
                    request.user.pk,
                    annotation_id=annotation_id
                )
                return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def st(self, request, pk=None):
        result, qt = timeit(
            get_sequence_type,
            [pk],
            request.user
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def st_blast(self, request, pk=None):
        result, qt = timeit(
            get_mlst_blast_results,
            [pk],
            request.user
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def st_allele(self, request, pk=None):
        result, qt = timeit(
            get_mlst_allele_matches,
            [pk],
            request.user
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def cgmlst(self, request, pk=None):
        result, qt = timeit(
            get_cgmlst,
            [pk],
            request.user
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def variant_count(self, request, pk=None):
        result, qt = timeit(
            get_variant_counts,
            [pk],
            request.user.pk
        )
        return self.formatted_response(result, query_time=qt)

    @detail_route(methods=['get'])
    def virulence(self, request, pk=None):
        result, qt = timeit(
            get_ariba_virulence,
            [pk],
            request.user.pk
        )
        return self.formatted_response(result, query_time=qt)


class MetadataViewSet(CustomReadOnlyModelViewSet):
    """Metadata related viewset."""

    queryset = Metadata.objects.all()
    serializer_class = MetadataSerializer

    def list(self, request):
        """
        Stored metadata information for a given sample.
        """
        urls = {
            'msg': 'Must use bulk_by_sample to get metadata information',
        }

        return Response(urls)

    @list_route(methods=['post'])
    def bulk_by_sample(self, request):
        """Given a list of Sample IDs, return metadata for each Sample."""
        if request.method == 'POST':
            validator = validate_list_of_ids(request.data, max_query=500)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })

            result, qt = timeit(get_sample_metadata, request.data['ids'],
                                request.user.pk)
            return self.formatted_response(result, query_time=qt)

'''
class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Publications.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        return Response(get_tags_by_sample(pk))


class ResistanceViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Resistances.
    """
    queryset = Resistance.objects.all()
    serializer_class = ResistanceSerializer

    def list(self, request):
        if 'antibiotic' in request.GET:
            if 'test' in request.GET:
                queryset = Resistance.objects.filter(
                    antibiotic__iexact=request.GET['antibiotic'],
                    test__iexact=request.GET['test']
                )
            else:
                queryset = Resistance.objects.filter(
                    antibiotic__iexact=request.GET['antibiotic']
                )
        else:
            queryset = Resistance.objects.all()

        if len(queryset) == 1:
            serializer = ResistanceSerializer(queryset[0])
            return Response(serializer.data)
        else:
            return self.paginate(queryset, serializer=TagSerializer)

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
                query = None
                if 'resistance_id' in request.GET:
                    query = request.GET['resistance_id']
                return self.formatted_response(get_resistance_by_samples(
                    request.data['ids'], resistance_id=query
                ))
'''
