"""Insert variant analysis results into database."""
from itertools import islice
from django.core.management.base import BaseCommand, CommandError

from api.utils import (
    get_annotated_snps_by_sample,
    get_annotated_indels_by_sample
)

from sample.models import Sample
from variant.models import Reference


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('reference', metavar='REFERENCE',
                            help=('Genome to use a reference.'))
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help=('Sample Tag to create variant genome.'))

    def handle(self, *args, **opts):
        """Insert results to database."""
        try:
            reference = Reference.objects.get(name=opts['reference'])
        except Reference.DoesNotExist:
            raise CommandError('Missing Reference: {0} == Exiting.'.format(
                opts['reference']
            ))

        try:
            sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('Sample {0} Does Not Exist'.format(
                opts['sample_tag']
            ))

        self.variants = {}
        self.process_variants(self.get_snps(sample.pk))
        self.process_variants(self.get_indels(sample.pk), is_snp=False)
        self.get_alternate_genome(reference.sequence)
        self.last_position = len(self.alternate_genome.keys())

        print('position\treference\talternate\tis_variant\tvariant_kmer')
        for position, base in sorted(self.alternate_genome.items()):
            kmer = '-'
            if base['is_variant']:
                kmer = self.build_kmer(position)

            print('{0}\t{1}\t{2}\t{3}\t{4}'.format(
                position,
                base['reference_base'],
                base['alternate_base'],
                base['is_variant'],
                kmer
            ))

    def build_kmer(self, position, length=15):
        """Build kmer with variant at center."""
        start = self.build_start_seqeunce(position - 1, length)
        end = self.build_end_sequence(position + 1, length)
        kmer = '{0}{1}{2}'.format(
            start,
            self.alternate_genome[position]['alternate_base'],
            end
        )

        expected_length = length + length + 1
        if len(kmer) > expected_length:
            kmers = ["".join(i) for i in self.split_into_kmers(kmer, expected_length)]
            kmer = ",".join(kmers)
        elif len(kmer) < expected_length:
            raise CommandError(
               ('Kmer is less than the expected length of {0}'
                '. position: {1} ... kmer: {2}').format(
                    expected_length,
                    position,
                    kmer
                )
            )

        return kmer

    def split_into_kmers(self, seq, k):
        """
        Source: http://stackoverflow.com/questions/7636004/python-split-string-in-moving-window
        Returns a sliding window (of width n) over data from the iterable
           s -> (s0,s1,...s[n-1]), (s1,s2,...,sn),
        """
        it = iter(seq)
        result = tuple(islice(it, k))
        if len(result) == k:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result

    def build_start_seqeunce(self, position, length):
        seq = []

        while len("".join(seq)) < length:
            base = self.alternate_genome[position]['alternate_base']
            if base != '-':
                seq.append(base)
            position -= 1

            if position == 0:
                position = self.last_position

        seq.reverse()
        return "".join(seq)

    def build_end_sequence(self, position, length):
        seq = []

        while len("".join(seq)) < length:
            base = self.alternate_genome[position]['alternate_base']
            if base != '-':
                seq.append(base)
            position += 1

            if position > self.last_position:
                position = 1

        return "".join(seq)

    def get_alternate_genome(self, sequence, log=None):
        "Produce an alternate genome"
        self.alternate_genome = {}
        position = 1
        deleted_bases = []
        deletion_is_next = False
        is_deletion = False
        for base in sequence:
            reference_base = base
            alternate_base = base
            is_variant = False

            if position in self.variants:
                reference_base = self.variants[position]['reference_base']
                alternate_base = self.variants[position]['alternate_base']
                is_variant = True
                if self.variants[position]['is_snp']:
                    # SNP
                    if base != reference_base:
                        self.raise_reference_match_error(
                            position, base, reference_base
                        )
                elif len(reference_base) > 1:
                    # Deletion
                    if base != reference_base[0]:
                        self.raise_reference_match_error(
                            position, base, reference_base
                        )
                    deletion_is_next = True
                    deleted_bases = reference_base[1:]
                else:
                    # Insertion
                    if base != alternate_base[0]:
                        self.raise_reference_match_error(
                            position, base, alternate_base
                        )

            if is_deletion:
                if base != deleted_bases[0]:
                    self.raise_reference_match_error(
                        position, base, deleted_bases[0]
                    )
                else:
                    alternate_base = '-'
                    if len(deleted_bases) == 1:
                        is_deletion = False
                    else:
                        deleted_bases = deleted_bases[1:]

            self.alternate_genome[position] = {
                'reference_base': reference_base,
                'alternate_base': alternate_base,
                'is_variant': is_variant
            }

            if deletion_is_next:
                is_deletion = True
                deletion_is_next = False
            position += 1

    def raise_reference_match_error(self, position, ref, sample):
        raise CommandError(
           ('Reference bases do not match at position {0}'
            '. REF: {1} ... Sample: {2}').format(
                position,
                ref,
                sample
            )
        )

    def build_reference(self, sequence):
        self.sequence = {}
        position = 1
        for base in sequence:
            self.sequence[position] = base
            position += 1

    def get_snps(self, sample_id):
        return get_annotated_snps_by_sample(sample_id)

    def get_indels(self, sample_id):
        return get_annotated_indels_by_sample(sample_id)

    def process_variants(self, variants, is_snp=True):
        for variant in variants:
            if variant['reference_position'] not in self.variants:
                self.variants[variant['reference_position']] = {
                    'reference_base': variant['reference_base'],
                    'alternate_base': variant['alternate_base'],
                    'confidence': variant['confidence'],
                    'is_snp': is_snp
                }
            else:
                raise CommandError(
                    ('Duplicate variants at reference position {0}').format(
                        variant['reference_position']
                    )
                )
