from django.contrib.auth.models import User
# from django.db.models import Q

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
from api.serializers.assemblies import AssemblyStatSerializer, ContigSerializer
from api.serializers.sccmecs import (
    SCCmecCoverageSerializer,
    SCCmecPrimerSerializer,
    SCCmecProteinSerializer
)
from api.serializers.sequence_types import BlastSerializer, Srst2Serializer
from api.serializers.sequences import SequenceStatSerializer

from api.utils import (
    get_genes_by_sample,
    get_indels_by_sample,
    get_resistance_by_samples,
    get_samples,
    get_samples_by_tag,
    get_sccmec_primers_by_sample,
    get_sccmec_coverage_by_sample,
    get_sccmec_subtypes_by_sample,
    get_snps_by_sample,
    get_tags_by_sample,
    get_public_samples
)

from api.validators import validate_positive_integer, validate_list_of_ids

from sample.models import Publication, Sample, Tag, Resistance
from assembly.models import Stats, Contigs
from mlst.models import Srst2, Blast
from sequence.models import Stat
from sccmec.models import Coverage, Primers, Proteins


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
            return self.paginate(get_samples(sample_id=pk), is_serialized=True)

    def list(self, request):
        if 'st' in request.GET:
            validator = validate_positive_integer(request.GET['st'])
            if validator['has_errors']:
                return Response(validator)
            else:
                ids = None
                if 'is_exact' in request.GET:
                    ids = Srst2.objects.filter(
                        st_stripped=request.GET['st'], is_exact=True
                    ).values_list('sample_id', flat=True)
                else:
                    ids = Srst2.objects.filter(
                        st_stripped=request.GET['st']
                    ).values_list('sample_id', flat=True)
                queryset = get_samples(sample_ids=ids)
        else:
            queryset = get_samples()


        '''
        if not request.user.is_superuser:
            queryset = Sample.objects.filter(
                Q(is_public=True) | Q(user_id=request.user.pk)
            )
        '''
        return self.paginate(queryset, is_serialized=True)

    @list_route(methods=['get'])
    def public(self, request):
        """Given a list of SNP IDs, return table info for each SNP."""
        if 'is_published' in request.GET:
            samples = get_public_samples(is_published=True)
        else:
            samples = get_public_samples()

        return self.paginate(samples, page_size=250, is_serialized=True)

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        return self.formatted_response(get_tags_by_sample(pk))

    @detail_route(methods=['get'])
    def assembly(self, request, pk=None):
        hits = Stats.objects.filter(sample_id=pk)
        serializer = AssemblyStatSerializer(hits, many=True)
        return self.formatted_response(serializer.data)

    @detail_route(methods=['get'])
    def contigs(self, request, pk=None):
        hits = Contigs.objects.filter(sample_id=pk)
        serializer = ContigSerializer(hits, many=True)
        return self.formatted_response(serializer.data)

    @detail_route(methods=['get'])
    def genes(self, request, pk=None):
        if 'product_id' in request.GET and 'cluster_id' in request.GET:
            product = validate_positive_integer(request.GET['product_id'])
            cluster = validate_positive_integer(request.GET['cluster_id'])
            if product['has_errors']:
                return Response(product)
            elif cluster['has_errors']:
                return Response(cluster)
            else:
                return self.paginate(
                    get_genes_by_sample(
                        pk,
                        product_id=request.GET['product_id'],
                        cluster_id=request.GET['cluster_id']
                    ),
                    page_size=250,
                    is_serialized=True
                )
        elif 'product_id' in request.GET:
            validator = validate_positive_integer(request.GET['product_id'])
            if validator['has_errors']:
                return Response(validator)
            else:
                return self.paginate(
                    get_genes_by_sample(
                        pk, product_id=request.GET['product_id']
                    ),
                    page_size=250,
                    is_serialized=True
                )
        elif 'cluster_id' in request.GET:
            validator = validate_positive_integer(request.GET['cluster_id'])
            if validator['has_errors']:
                return Response(validator)
            else:
                return self.paginate(
                    get_genes_by_sample(
                        pk, cluster_id=request.GET['cluster_id']
                    ),
                    page_size=250,
                    is_serialized=True
                )
        else:
            return self.paginate(
                get_genes_by_sample(pk), page_size=250,
                is_serialized=True
            )

    @detail_route(methods=['get'])
    def indels(self, request, pk=None):
        return self.formatted_response(get_indels_by_sample(pk))

    @detail_route(methods=['get'])
    def qc(self, request, pk=None):
        hits = Stat.objects.filter(sample_id=pk)
        serializer = SequenceStatSerializer(hits, many=True)
        return self.formatted_response(serializer.data)

    @detail_route(methods=['get'])
    def sccmec_coverages(self, request, pk=None):
        return self.formatted_response(get_sccmec_coverage_by_sample(pk))

    @detail_route(methods=['get'])
    def sccmec_primers(self, request, pk=None):
        if 'exact_hits' in request.GET:
            return self.formatted_response(
                get_sccmec_primers_by_sample(pk, exact_hits=True)
            )
        elif 'predict' in request.GET:
            return self.formatted_response(
                get_sccmec_primers_by_sample(pk, predict=True)
            )
        else:
            return self.formatted_response(get_sccmec_primers_by_sample(pk))

    @detail_route(methods=['get'])
    def sccmec_subtypes(self, request, pk=None):
        if 'exact_hits' in request.GET:
            return self.formatted_response(
                get_sccmec_subtypes_by_sample(pk, exact_hits=True)
            )
        elif 'predict' in request.GET:
            return self.formatted_response(
                get_sccmec_subtypes_by_sample(pk, predict=True)
            )
        else:
            return self.formatted_response(get_sccmec_subtypes_by_sample(pk))

    @detail_route(methods=['get'])
    def sccmec_proteins(self, request, pk=None):
        hits = Proteins.objects.filter(sample_id=pk)
        serializer = SCCmecProteinSerializer(hits, many=True)
        return self.formatted_response(serializer.data)

    @detail_route(methods=['get'])
    def snps(self, request, pk=None):
        validator = validate_positive_integer(pk)
        if validator['has_errors']:
            return Response(validator, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return self.formatted_response(get_snps_by_sample(pk))

    @detail_route(methods=['get'])
    def st_blast(self, request, pk=None):
        hits = Blast.objects.filter(sample_id=pk)
        serializer = BlastSerializer(hits, many=True)
        return self.formatted_response(serializer.data)

    @detail_route(methods=['get'])
    def st_srst2(self, request, pk=None):
        hits = Srst2.objects.filter(sample_id=pk)
        serializer = Srst2Serializer(hits, many=True)
        return self.formatted_response(serializer.data)


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
                return self.formatted_response(get_resitance_by_samples(
                    request.data['ids'], resistance_id=query
                ))
