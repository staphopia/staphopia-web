"""Insert variant analysis results into database."""
from itertools import islice
import tempfile
from django.core.management.base import BaseCommand, CommandError

from api.utils import (
    get_annotated_snps_by_sample,
    get_annotated_indels_by_sample
)

from sample.models import Sample
from staphopia.utils import jf_query
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
        parser.add_argument('jellyfish', metavar='JELLYFISH',
                            help=('Location to Jellyfish counts.'))
        parser.add_argument('--printall', action='store_true',
                            help='Prints everything variants and non.')

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

        # Get kmers of the variants
        self.kmers = {}
        for position, base in sorted(self.alternate_genome.items()):
            if base['is_variant'] or opts['printall']:
                kmers = self.build_kmer(position, opts['jellyfish'])
                self.alternate_genome[position]['kmers'] = kmers
                for kmer in kmers:
                    self.kmers[kmer] = "NOT_FOUND"

        # verify kmers against jellyfish counts
        self.verify_kmers(opts['jellyfish'])

        # Print the results
        cols = ['position', 'reference', 'alternate', 'is_variant',
                'is_snp', 'is_insertion', 'coverage', 'genotype_quality',
                'qual_by_depth', 'raw_quality', 'variant_kmer',
                'jellyfish_counts']
        print("\t".join(cols))
        for position, base in sorted(self.alternate_genome.items()):
            if base['is_variant']:
                counts = []
                for kmer in self.alternate_genome[position]['kmers']:
                    counts.append(self.kmers[kmer])

                print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}'.format(
                    position,
                    base['reference_base'],
                    base['alternate_base'],
                    base['is_variant'],
                    base['is_snp'],
                    base['is_insertion'],
                    base['confidence']['DP'],
                    base['confidence']['GQ'],
                    base['confidence']['QD'],
                    base['confidence']['quality'],
                    ",".join(self.alternate_genome[position]['kmers']),
                    ",".join(counts),
                ))
            elif opts['printall']:
                counts = []
                for kmer in self.alternate_genome[position]['kmers']:
                    counts.append(self.kmers[kmer])
                print('{0}\t{1}\t{2}\t{3}\tFalse\tFalse\t-\t-\t-\t-\t{4}\t{5}'.format(
                    position,
                    base['reference_base'],
                    base['alternate_base'],
                    base['is_variant'],
                    ",".join(self.alternate_genome[position]['kmers']),
                    ",".join(counts)
                ))

    def build_kmer(self, position, jf, length=15):
        """Build kmer with variant at center."""
        start = self.build_start_seqeunce(position - 1, length)
        end = self.build_end_sequence(position + 1, length)
        if self.alternate_genome[position]['alternate_base'] == "-":
            return ['SNP/InDel Overlap']
        kmer = '{0}{1}{2}'.format(
            start,
            self.alternate_genome[position]['alternate_base'],
            end
        )

        total = length + length + 1
        if len(kmer) > total:
            kmer = ["".join(i) for i in self.split_into_kmers(kmer, total)]
        elif len(kmer) < total:
            raise CommandError(
               ('Kmer is less than the expected length of {0}'
                '. position: {1} ... kmer: {2}').format(
                    total,
                    position,
                    kmer
                )
            )
        else:
            kmer = [kmer]

        return kmer

    def verify_kmers(self, jf):
        """Get count of kmer via jellyfish."""
        jf_output = None
        with tempfile.NamedTemporaryFile() as temp:
            for kmer in self.kmers.keys():
                if kmer.startswith('SNP/InDel'):
                    pass
                else:
                    temp.write('>{0}\n{0}\n'.format(kmer))
                    temp.write('>{0}\n{0}\n'.format(
                        self.reverse_complement(kmer)
                    ))

            temp.flush()
            jf_output = jf_query(jf, temp.name)

        for line in jf_output.split('\n'):
            if not line:
                continue
            kmer, count = line.rstrip().split(' ')
            if kmer not in self.kmers:
                self.kmers[self.reverse_complement(kmer)] = count
            else:
                self.kmers[kmer] = count

    def reverse_complement(self, seq):
        """Reverse complement a DNA sequence."""
        complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        return ''.join([complement[b] for b in seq[::-1]])

    def split_into_kmers(self, seq, k):
        """
        Source: http://stackoverflow.com/questions/7636004/                   \
                     python-split-string-in-moving-window
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
        if position == 0:
            position = self.last_position

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
        if position > self.last_position:
            position = 1

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
            confidence = None
            is_variant = False
            is_snp = False
            is_insertion = False

            if position in self.variants:
                reference_base = self.variants[position]['reference_base']
                alternate_base = self.variants[position]['alternate_base']
                confidence = self.variants[position]['confidence']
                is_variant = True
                if self.variants[position]['is_snp']:
                    # SNP
                    is_snp = True
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
                    is_insertion = True
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
                'is_variant': is_variant,
                'is_snp': is_snp,
                'is_insertion': is_insertion,
                'confidence': confidence,
                'kmers': "",
                'counts': "",
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