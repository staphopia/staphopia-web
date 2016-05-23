from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.serializers.samples import (
    PublicationSerializer,
    SampleSerializer,
    TagSerializer
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
    format_results,
    get_gene_features_by_sample,
    get_indels_by_sample,
    get_samples_by_tag,
    get_snps_by_sample,
    get_tags_by_sample
)

from sample.models import Publication, Sample, Tag
from assembly.models import Stats, Contigs
from mlst.models import Srst2, Blast
from sequence.models import Stat
from sccmec.models import Coverage, Primers, Proteins


class SampleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer

    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        return Response(get_tags_by_sample(pk))

    @detail_route(methods=['get'])
    def assembly_stats(self, request, pk=None):
        hits = Stats.objects.filter(sample_id=pk)
        serializer = AssemblyStatSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def contigs(self, request, pk=None):
        hits = Contigs.objects.filter(sample_id=pk)
        serializer = ContigSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def genes(self, request, pk=None):
        return Response(get_gene_features_by_sample(pk))

    @detail_route(methods=['get'])
    def indels(self, request, pk=None):
        return Response(get_indels_by_sample(pk))

    @detail_route(methods=['get'])
    def sccmec_coverages(self, request, pk=None):
        hits = Coverage.objects.filter(sample_id=pk)
        serializer = SCCmecCoverageSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def sccmec_primers(self, request, pk=None):
        hits = Primers.objects.filter(sample_id=pk)
        serializer = SCCmecPrimerSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def sccmec_proteins(self, request, pk=None):
        hits = Proteins.objects.filter(sample_id=pk)
        serializer = SCCmecProteinSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def sequence_quality(self, request, pk=None):
        hits = Stat.objects.filter(sample_id=pk)
        serializer = SequenceStatSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def snps(self, request, pk=None):
        return Response(get_snps_by_sample(pk))

    @detail_route(methods=['get'])
    def st_blast(self, request, pk=None):
        hits = Blast.objects.filter(sample_id=pk)
        serializer = BlastSerializer(hits, many=True)
        return Response(format_results(serializer.data))

    @detail_route(methods=['get'])
    def st_srst2(self, request, pk=None):
        hits = Srst2.objects.filter(sample_id=pk)
        serializer = Srst2Serializer(hits, many=True)
        return Response(format_results(serializer.data))


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Samples.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        return Response(get_samples_by_tag(pk))


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for listing or retrieving Publications.
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

    @detail_route(methods=['get'])
    def samples(self, request, pk=None):
        return Response(get_tags_by_sample(pk))
