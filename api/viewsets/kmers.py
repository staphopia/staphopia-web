"""Viewsets related to Kmer tables."""
import time

from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from api.pagination import CustomReadOnlyModelViewSet
from api.utils import get_kmer_by_sequence, get_kmer_by_partition
from api.validators import validate_list_of_ids
from kmer.models import Total
from api.serializers.kmers import KmerTotalSerializer


class KmerViewSet(CustomReadOnlyModelViewSet):
    """A simple ViewSet for listing or retrieving Kmers."""

    queryset = Total.objects.all()
    serializer_class = KmerTotalSerializer

    @list_route(methods=['post'])
    def by_partition(self, request):
        """Given a parition, Kmers, samples IDs, return counts."""
        if request.method == 'POST':
            start = time.time()
            validator = validate_list_of_ids(request.data,
                                             max_query=50000)
            if validator['has_errors']:
                return Response({
                    "message": validator['message'],
                    "data": request.data
                })
            else:
                return self.formatted_response(get_kmer_by_partition(
                    request.data['extra']['partition'],
                    request.data['extra']['kmers'],
                    set(request.data['ids'])
                ), return_empty=True)

    @list_route(methods=['get'])
    def kmer_test(self, request, pk=None):
        import time
        start = time.time()
        sequence = 'ATGCGAAGCGACATGATCAAAAAAGGAGATCACCAAGCACCAGCAAGAAGTCTTTTACATGCCACGGGCGCGCTAAAAAGTCCAACTGATATGAACAAACCATTTGTAGCTATTTGTAACTCTTATATTGATATTGTTCCTGGACATGTTCATTTAAGAGAGCTTGCAGATATAGCTAAAGAAGCAATTAGAGAAGCCGGTGCCATTCCATTTGAATTCAATACAATTGGTGTTGATGATGGAATAGCTATGGGACATATCGGAATGCGATATTCTCTACCATCACGTGAAATTATTGCAGATGCAGCTGAAACTGTAATTAACGCTCATTGGTTTGACGGCGTATTTTACATTCCTAATTGTGACAAGATTACACCCGGTATGATTTTAGCAGCCATGAGGACAAACGTACCAGCTATCTTTTGCTCTGGTGGACCAATGAAAGCTGGCTTATCTGCACATGGAAAAGCATTAACACTTTCATCAATGTTTGAAGCAGTCGGCGCATTTAAAGAAGGATCGATTTCTAAAGAAGAATTTTTAGATATGGAACAAAATGCCTGCCCTACTTGTGGTTCATGTGCTGGGATGTTTACTGCAAATTCAATGAACTGTTTGATGGAAGTTTTAGGTCTAGCATTACCATACAACGGTACTGCACTTGCAGTCAGTGATCAACGACGCGAAATGATTCGCCAAGCAGCTTTTAAATTAGTTGAAAATATTAAAAATGATTTAAAACCACGTGATATCGTTACTCGCGAAGCAATTGATGATGCATTTGCACTTGATATGGCTATGGGTGGTTCAACAAACACAGTACTGCATACGTTAGCCATTGCCAATGAAGCTGGTATTGATTATGACTTAGAGCGCATTAATGCTATTGCCAAACGCACGCCATATTTATCAAAAATAGCACCTAGTTCATCGTATTCAATGCATGATGTGCATGAAGCTGGTGGCGTCCCAGCAATTATTAATGAATTGATGAAGAAAGATGGCACGTTACACCCAGATAGAATCACAGTTACTGGCAAAACGTTACGTGAAAATAACGAAGGCAAAGAAATTAAGAACTTTGATGTCATTCACCCTCTTGATGCACCATATGATGCACAAGGCGGTTTATCTATCTTATTTGGTAATATCGCCCCTAAAGGCGCAGTTATTAAAGTTGGCGGCGTTGATCCATCTATCAAAACATTTACTGGGAAAGCAATTTGTTTCAATTCGCATGATGAAGCTGTTGAAGCAATAGACAATCGTACCGTTCGTGCAGGCCACGTCGTTGTCATTAGATATGAAGGACCTAAAGGTGGACCAGGTATGCCTGAAATGTTAGCACCTACTTCCTCTATTGTTGGTCGCGGCTTAGGTAAAGATGTTGCATTAATTACTGATGGGCGTTTTTCCGGTGCCACAAGAGGTATTGCAGTTGGTCATATTTCCCCTGAAGCTGCATCTGGTGGACCAATTGCCTTAATTGAAGATGGAGATGAGATTACTATTGATTTAACAAATCGTACATTAAACGTAAACCAGCCTGAAGATGTTCTAGCGCGTCGCCGAGAATCTTTAACACCATTTAAAGCGAAAGTAAAAACAGGTTATCTAGCTCGTTATACTGCCCTAGTAACTAGCGCAAATACAGGTGGCGTCATGCAAGTCCCTGAGAATTTAATTTAA'
        results = get_kmer_by_sequence(sequence, [3545, 3546, 3547, ])
        time = '{0}ms'.format(
            int(
                (time.time() - start) * 1000.0
            )
        )
        return self.formatted_response(results, time=time)

    @list_route(methods=['get'])
    def partitions(self, request, pk=None):
        from kmer.partitions import PARTITIONS
        return Response(PARTITIONS)
