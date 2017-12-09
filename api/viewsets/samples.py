from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.serializers.samples import (
    PublicationSerializer,
    SampleSerializer,
    TagSerializer,
    ResistanceSerializer
)

from api.queries.assemblies import get_assembly_stats, get_assembled_contigs
from api.queries.samples import (
    get_resistance_by_samples,
    get_samples,
    get_samples_by_tag,
    get_tags_by_sample,
    get_public_samples,
    get_sample_metadata
)

from api.queries.genes import get_genes_by_sample
from api.queries.sequences import get_sequencing_stats
from api.queries.sequence_types import (
    get_unique_st_samples,
    get_blast_sequence_type,
    get_srst2_sequence_type
)

from api.queries.sccmecs import (
    get_sccmec_primers_by_sample,
    get_sccmec_coverage_by_sample,
    get_sccmec_proteins_by_sample
)
from api.queries.variants import get_indels_by_sample, get_snps_by_sample

from api.validators import validate_positive_integer, validate_list_of_ids

from sample.models import Publication, Sample, Tag, Resistance


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
        if 'st' in request.GET:
            validator = validate_positive_integer(request.GET['st'])
            if validator['has_errors']:
                return Response(validator)
            else:
                ids = None
                '''
                if 'is_exact' in request.GET:
                    ids = Srst2.objects.filter(
                        st_stripped=request.GET['st'], is_exact=True
                    ).values_list('sample_id', flat=True)
                else:
                    ids = Srst2.objects.filter(
                        st_stripped=request.GET['st']
                    ).values_list('sample_id', flat=True)
                '''
                queryset = get_samples(request.user.pk, sample_ids=ids)
        elif 'user_only' in request.GET:
            queryset = get_samples(request.user.pk, user_only=True)
        else:
            queryset = get_samples(request.user.pk)

        return self.paginate(queryset, is_serialized=True)

    @list_route(methods=['get'])
    def public(self, request):
        """Return all public ENA samples."""
        samples = None
        if 'include_location' in request.GET:
            samples = get_public_samples(include_location=True)
        else:
            samples = get_public_samples()
        return self.paginate(samples, page_size=500, is_serialized=True)

    @list_route(methods=['get'])
    def published(self, request):
        """Return all published ENA samples."""
        samples = get_public_samples(is_published=True)

        return self.paginate(samples, page_size=500, is_serialized=True)

    @list_route(methods=['get'])
    def unique_st(self, request):
        """Return all public ENA samples with a unique ST."""
        samples = get_unique_st_samples()

        return self.paginate(samples, page_size=500, is_serialized=True)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        return self.formatted_response(get_tags_by_sample(pk, request.user.pk))

    @detail_route(methods=['get'])
    def assembly(self, request, pk=None):
        return self.formatted_response(get_assembly_stats(
            [pk],
            request.user.pk,
            is_scaffolds='TRUE' if 'scaffolds' in request.GET else 'FALSE',
            is_plasmids='TRUE' if 'plasmids' in request.GET else 'FALSE'
        ))

    @detail_route(methods=['get'])
    def contigs(self, request, pk=None):
        return self.formatted_response(get_assembled_contigs(
            [pk],
            request.user.pk,
            is_plasmids='TRUE' if 'plasmids' in request.GET else 'FALSE'
        ))

    @detail_route(methods=['get'])
    def genes(self, request, pk=None):
        product = None
        cluster = None
        if 'product_id' in request.GET:
            product = validate_positive_integer(request.GET['product_id'])
            if product['has_errors']:
                return Response(product)
            else:
                product = request.GET['product_id']

        if 'cluster_id' in request.GET:
            cluster = validate_positive_integer(request.GET['cluster_id'])
            if cluster['has_errors']:
                return Response(cluster)
            else:
                cluster = request.GET['cluster_id']

        return self.paginate(
            get_genes_by_sample(
                [pk],
                request.user.pk,
                product_id=product,
                cluster_id=cluster
            ),
            page_size=250,
            is_serialized=True
        )

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
                return self.formatted_response(
                    get_indels_by_sample([pk], request.user.pk,
                                         annotation_id=annotation_id)
                )

    @detail_route(methods=['get'])
    def metadata(self, request, pk=None):
        return self.formatted_response(get_sample_metadata(pk))

    @detail_route(methods=['get'])
    def qc(self, request, pk=None):
        return self.formatted_response(get_sequencing_stats(
            [pk],
            request.user.pk,
            is_original='TRUE' if 'original' in request.GET else 'FALSE',
            qual_per_base=True if 'bases' in request.GET else False,
            read_lengths=True if 'lengths' in request.GET else False
        ))

    @detail_route(methods=['get'])
    def sccmec_coverages(self, request, pk=None):
        return self.formatted_response(get_sccmec_coverage_by_sample(
            [pk],
            request.user.pk
        ))

    @detail_route(methods=['get'])
    def sccmec_primers(self, request, pk=None):
        return self.formatted_response(get_sccmec_primers_by_sample(
            [pk],
            request.user.pk,
            exact_hits=True if 'exact_hits' in request.GET else False,
            predict=True if 'predict' in request.GET else False
        ))

    @detail_route(methods=['get'])
    def sccmec_subtypes(self, request, pk=None):
        return self.formatted_response(get_sccmec_primers_by_sample(
            [pk],
            request.user.pk,
            is_subtypes=True,
            exact_hits=True if 'exact_hits' in request.GET else False,
            predict=True if 'predict' in request.GET else False
        ))

    @detail_route(methods=['get'])
    def sccmec_proteins(self, request, pk=None):
        return self.formatted_response(get_sccmec_proteins_by_sample(
            [pk],
            request.user.pk
        ))

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
                return self.formatted_response(
                    get_snps_by_sample([pk], request.user.pk,
                                       annotation_id=annotation_id)
                )

    @detail_route(methods=['get'])
    def st_blast(self, request, pk=None):
        return self.formatted_response(get_blast_sequence_type(
            [pk], request.user.pk
        ))

    @detail_route(methods=['get'])
    def st_srst2(self, request, pk=None):
        return self.formatted_response(get_srst2_sequence_type(
            [pk], request.user.pk
        ))


class TagViewSet(CustomReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request):
        if 'tag' in request.GET:
            queryset = Tag.objects.filter(tag=request.GET['tag'])
        else:
            queryset = Tag.objects.all()

        if len(queryset) == 1:
            serializer = TagSerializer(queryset[0])
            return Response(serializer.data)
        else:
            return self.paginate(queryset, serializer=TagSerializer)

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        return self.formatted_response(get_samples_by_tag(pk))


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


class MetaDataViewSet(CustomReadOnlyModelViewSet):
    """Metadata related viewset."""

    queryset = ''

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
            else:
                return self.formatted_response(get_sample_metadata(
                    request.data['ids'], single=False
                ))
