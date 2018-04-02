"""Insert variant analysis results into database."""
from collections import OrderedDict
from itertools import islice
import json
import sys
import tempfile

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from api.queries.variants import (
    get_annotated_snps_by_sample,
    get_annotated_indels_by_sample
)

from api.queries.tags import get_samples_by_tag
from api.queries.variants import get_variant_annotation
from api.utils import query_database

from sample.models import Sample
from staphopia.utils import jf_query, timeit
from variant.models import Reference, ReferenceGenome, SNP


@timeit
def get_variant_positions(reference_id, table='snp'):
    variants = OrderedDict()
    sql = """SELECT id, reference_position
             FROM variant_{0}
             WHERE reference_id={1};""".format(table, reference_id)
    for row in query_database(sql):
        variants[row['id']] = row['reference_position']

    return variants


def get_variants(sample, snp_position, indel_position, reference_id, user_id):
    variants = OrderedDict()
    sql = """SELECT v.sample_id, v.snp, v.indel
             FROM variant_variant AS v
             LEFT JOIN sample_basic AS s
             ON v.sample_id=s.sample_id
             WHERE v.sample_id = {0} AND v.reference_id={1} AND
                   (s.is_public=TRUE OR s.user_id={2});""".format(
        sample, reference_id, user_id
    )
    for row in query_database(sql):
        for snp in row['snp']:
            pos = snp_position[snp['snp_id']]
            if pos not in variants:
                snp['is_snp'] = True
                variants[pos] = snp
            else:
                raise CommandError(
                    f"Error {sample['name']} {pos} overlapping variants"
                )

        for indel in row['indel']:
            pos = indel_position[indel['indel_id']]
            if pos not in variants:
                indel['is_snp'] = False
                variants[pos] = indel
            else:
                raise CommandError(
                    f"Error {sample['name']} {pos} overlapping variants"
                )
    return variants


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('tag', metavar='TAG',
                            help=('Tag to get samples.'))
        parser.add_argument('summary', metavar='SUMMARY',
                            help=('Variant annotation summary for samples.'))
        parser.add_argument('staphopia', metavar='STAPHOPIA',
                            help=('Base location of analysis results.'))
        parser.add_argument('--reference', metavar='REFERENCE',
                            default='gi|29165615|ref|NC_002745.2|',
                            help=('Reference genome.'))
        parser.add_argument('--pass_only', action='store_true',
                            help='Only print annotation IDs that pass.')
        parser.add_argument('--all_variants', action='store_true',
                            help='Include InDels as well.')
        parser.add_argument('--printall', action='store_true',
                            help='Prints everything variants and non.')
        parser.add_argument('--nokmers', action='store_true',
                            help='Skip printing kmers.')

    def handle(self, *args, **opts):
        """Insert results to database."""
        # Get User
        user = User.objects.get(username='ena')

        # Get Samples
        samples = OrderedDict()
        for sample in get_samples_by_tag(opts['tag'], is_id=False):
            samples[sample['sample_id']] = sample

        # Read annotation summary
        summary = {}
        col_names = None
        with open(opts['summary'], 'r') as fh:
            for line in fh:
                line = line.rstrip()
                if line.startswith('annotation_id'):
                    # annotation_id, locus_tag, samples, snps
                    # indels, snp_all_samples, has_indel, annotation_pass
                    col_names = line.split('\t')
                else:
                    row = dict(zip(col_names, line.split('\t')))
                    if opts['all_variants'] or not bool(row['has_indel']):
                        summary[row['annotation_id']] = row

        # Get annotations
        annotations = {}
        for annotation in get_variant_annotation(None):
            annotations[annotation['id']] = annotation
            annotations[annotation['id']]['position'] = []

        # Get Reference sequence
        try:
            reference_obj = Reference.objects.get(name=opts['reference'])
            reference_id = reference_obj.pk
            reference = ReferenceGenome.objects.get(
                reference=reference_obj
            ).sequence
        except Reference.DoesNotExist:
            raise CommandError('Missing Reference: {0} == Exiting.'.format(
                opts['reference']
            ))

        for position, vals in reference.items():
            annotations[vals['annotation_id']]['position'].append(position)

        # Get Variants Per Sample
        snp_positions = get_variant_positions(reference_id, table='snp')
        indel_positions = get_variant_positions(reference_id, table='indel')
        for sample_id, sample in samples.items():
            # Parse through variants for each sample
            variants = get_variants(sample_id, snp_positions, indel_positions,
                                    reference_id, user.pk)
            alternate_genome = self.generate_alternate_genome(
                variants, reference
            )
            print(len(alternate_genome), len(reference))

            # Get kmers of the variants
            total_kmers = {}
            for position, vals in sorted(alternate_genome.items()):
                if vals['is_variant'] or opts['printall']:
                    kmers = self.build_kmer(position)
                    alternate_genome[position]['kmers'] = kmers
                    for kmer in kmers:
                        if kmer == "SNP/InDel Overlap":
                            total_kmers[kmer] = "NOT_FOUND"
                        else:
                            total_kmers[kmer] = "NOT_FOUND"
                            total_kmers[self.reverse_complement(kmer)] = "NOT_FOUND"

            # verify kmers against jellyfish counts
            jf_database = "{0}/{1}/{2}/{2}/analyses/kmer/{2}.jf".format(
                opts['staphopia'],
                sample['name'][0:6],
                sample['name']
            )
            counted_kmers = self.verify_kmers(total_kmers, jf_database)
            parsed = json.loads(alternate_genome)
            print(json.dumps(parsed, indent=4, sort_keys=True))
            sys.exit()
            # Print the results
            cols = ['sample_id', 'position', 'reference', 'alternate',
                    'is_variant', 'is_snp', 'is_insertion', 'is_variant_cluster',
                    'is_genic', 'annotation_id', 'coverage', 'genotype_quality',
                    'qual_by_depth', 'raw_quality', 'variant_kmer', 'jf_counts',
                    'total_jf_count', 'has_zero_count']
            print("\t".join(cols))
            for position, base in sorted(self.alternate_genome.items()):
                if base['is_variant']:
                    counts, total, has_zero_count = self.process_kmers(position)
                    kmers = ",".join(self.alternate_genome[position]['kmers'])
                    if opts['nokmers']:
                        kmers = "-"
                    print(('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t'
                           '{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}\t'
                           '{17}').format(
                        self.sample_id,
                        position,
                        base['reference_base'],
                        base['alternate_base'],
                        base['is_variant'],
                        base['is_snp'],
                        base['is_insertion'],
                        base['is_variant_cluster'],
                        self.is_genic[position],
                        self.annotation_id[position],
                        base['confidence']['DP'],
                        base['confidence']['GQ'],
                        base['confidence']['QD'],
                        base['confidence']['quality'],
                        kmers,
                        ",".join(counts),
                        total,
                        has_zero_count
                    ))
                elif opts['printall']:
                    counts, total, has_zero_count = self.process_kmers(position)
                    kmers = ",".join(self.alternate_genome[position]['kmers'])
                    if opts['nokmers']:
                        kmers = "-"
                    print(('{0}\t{1}\t{2}\t{3}\t{4}\tFalse\tFalse\tFalse\t{5}\t'
                           '{6}\t-\t-\t-\t-\t{7}\t{8}\t{9}\t{10}').format(
                        self.sample_id,
                        position,
                        base['reference_base'],
                        base['alternate_base'],
                        base['is_variant'],
                        self.is_genic[position],
                        self.annotation_id[position],
                        kmers,
                        ",".join(counts),
                        total,
                        has_zero_count
                    ))
            break

    def generate_alternate_genome(self, variants, reference):
        """Produce an alternate genome"""
        alternate_genome = OrderedDict()
        deleted_bases = []
        deletion_is_next = False
        is_deletion = False
        for position, vals in reference.items():
            base = vals['base']
            reference_base = base
            alternate_base = base
            is_variant = False
            is_snp = False
            is_insertion = False

            if position in variants:
                reference_base = variants[position]['reference_base']
                alternate_base = variants[position]['alternate_base']
                is_variant = True
                if self.variants[position]['is_snp']:
                    # SNP
                    is_snp = True
                    if base != reference_base:
                        self.raise_reference_match_error(
                            position, base, reference_base,
                            variant_type='SNP'
                        )
                elif len(reference_base) > 1:
                    # Deletion
                    if base != reference_base[0]:
                        self.raise_reference_match_error(
                            position, base, reference_base,
                            variant_type='Deletion'
                        )
                    if not is_deletion:
                        deletion_is_next = True
                    else:
                        # Overlapping deletions, reset it and delete alt_base
                        is_deletion = False
                        alternate_base = '-'
                    deleted_bases = reference_base[1:]
                else:
                    # Insertion
                    is_insertion = True
                    if base != alternate_base[0]:
                        self.raise_reference_match_error(
                            position, base, alternate_base,
                            variant_type='Insert'
                        )

            if is_deletion:
                if base != deleted_bases[0]:
                    self.raise_reference_match_error(
                        position, base, deleted_bases[0],
                        variant_type='Deletion2'
                    )
                else:
                    alternate_base = '-'
                    if len(deleted_bases) == 1:
                        is_deletion = False
                        deleted_bases = []
                    else:
                        deleted_bases = deleted_bases[1:]

            alternate_genome[position] = {
                'reference_base': reference_base,
                'alternate_base': alternate_base,
                'is_variant': is_variant,
                'is_snp': is_snp,
                'is_insertion': is_insertion,
                'is_variant_cluster': False,
                'kmers': "",
                'counts': "",
            }

            if deletion_is_next:
                is_deletion = True
                deletion_is_next = False

        return alternate_genome

    def process_kmers(self, position):
        """Assess the counts for each kmer."""
        counts = []
        total = 0
        has_zero_count = False
        for kmer in self.alternate_genome[position]['kmers']:
            counts.append(str(self.kmers[kmer]))
            if self.kmers[kmer] != "NOT_FOUND":
                total += self.kmers[kmer]
                if self.kmers[kmer] == 0:
                    has_zero_count = True

        return [counts, total, has_zero_count]

    def build_kmer(self, position, length=15):
        """Build kmer with variant at center."""
        start, start_cluster = self.build_start_seqeunce(position - 1, length)
        end, end_cluster = self.build_end_sequence(position + 1, length)

        if start_cluster or end_cluster:
            self.alternate_genome[position]['is_variant_cluster'] = True

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

    def verify_kmers(self, kmers, jf):
        """Get count of kmer via jellyfish."""
        jf_output = None
        with tempfile.NamedTemporaryFile() as temp:
            for kmer in kmers.keys():
                if kmer.startswith('SNP/InDel'):
                    pass
                else:
                    temp.write('>{0}\n{0}\n'.format(kmer))

            temp.flush()
            jf_output = jf_query(jf, temp.name)

        for line in jf_output.split('\n'):
            if not line:
                continue
            kmer, count = line.rstrip().split(' ')
            count = int(count)
            kmers[self.reverse_complement(kmer)] = count
            kmers[kmer] = count
        return kmers

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
        is_variant_cluster = False
        if position == 0:
            position = self.last_position

        while len("".join(seq)) < length:
            base = self.alternate_genome[position]['alternate_base']
            if self.alternate_genome[position]['is_variant']:
                is_variant_cluster = True

            if base != '-':
                seq.append(base)
            position -= 1

            if position == 0:
                position = self.last_position

        seq.reverse()
        return ["".join(seq), is_variant_cluster]

    def build_end_sequence(self, position, length):
        seq = []
        is_variant_cluster = False
        if position > self.last_position:
            position = 1

        while len("".join(seq)) < length:
            base = self.alternate_genome[position]['alternate_base']
            if self.alternate_genome[position]['is_variant']:
                is_variant_cluster = True

            if base != '-':
                seq.append(base)
            position += 1

            if position > self.last_position:
                position = 1

        return ["".join(seq), is_variant_cluster]


    def raise_reference_match_error(self, position, ref, sample,
                                    variant_type=None):
        if variant_type:
            raise CommandError(
                   ('{3} ({4}): Reference bases do not match at position {0}'
                    '. REF: {1} ... Sample: {2}').format(
                        position,
                        ref,
                        sample,
                        self.sample_tag,
                        variant_type
                    )
                )
        else:
            raise CommandError(
               ('{3}: Reference bases do not match at position {0}'
                '. REF: {1} ... Sample: {2}').format(
                    position,
                    ref,
                    sample,
                    self.sample_tag
                )
            )

    def build_reference(self, sequence):
        self.sequence = {}
        position = 1
        for base in sequence:
            self.sequence[position] = base
            position += 1

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
