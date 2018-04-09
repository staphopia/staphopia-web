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

from api.queries.samples import get_samples
from api.queries.variants import get_variant_annotation
from api.utils import query_database

from sample.models import Sample
from staphopia.utils import jf_query, reverse_complement, timeit
from variant.models import Reference, ReferenceGenome, SNP
from variant.tools import (
    generate_alternate_genome
)


@timeit
def get_variant_positions(reference_id, table='snp'):
    variants = OrderedDict()
    sql = """SELECT id, reference_position, reference_base, alternate_base
             FROM variant_{0}
             WHERE reference_id={1};""".format(table, reference_id)
    for row in query_database(sql):
        variants[row['id']] = {
            'reference_position': row['reference_position'],
            'reference_base': row['reference_base'],
            'alternate_base': row['alternate_base']
        }

    with open(f'{table}-positions.json', 'w') as filehandle:
        json.dump(variants, filehandle)

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
            snp_id = snp_position[str(snp['snp_id'])]
            pos = snp_id['reference_position']
            if pos not in variants:
                snp['is_snp'] = True
                snp['reference_base'] = snp_id['reference_base']
                snp['alternate_base'] = snp_id['alternate_base']
                variants[pos] = snp
            else:
                raise CommandError(
                    f"Error {sample['name']} {pos} overlapping variants"
                )

        for indel in row['indel']:
            indel_id = indel_position[str(indel['indel_id'])]
            pos = indel_id['reference_position']
            if pos not in variants:
                indel['is_snp'] = False
                indel['reference_base'] = indel_id['reference_base']
                indel['alternate_base'] = indel_id['alternate_base']
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
        parser.add_argument('sample_id', metavar='SAMPLE_ID',
                            help=('Sample ID to extract genome from.'))
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
        for sample in get_samples(user.pk, sample_id=opts['sample_id']):
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
                    annotation_id = int(row['annotation_id'])
                    if opts['printall']:
                        summary[annotation_id] = row
                    elif row['has_indel'] == 'False':
                        summary[annotation_id] = row

        # Get annotations
        annotations = {}
        for annotation in get_variant_annotation(None):
            annotation_id = int(annotation['id'])
            annotations[annotation_id] = annotation
            annotations[annotation_id]['position'] = []

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
            annotations[int(vals['annotation_id'])]['position'].append(
                int(position)
            )

        for annotation_id in annotations:
            if annotation_id > 1:
                annotations[annotation_id]['start'] = min(
                    annotations[annotation_id]['position']
                )
                annotations[annotation_id]['end'] = max(
                    annotations[annotation_id]['position']
                )

        # Get Variants Per Sample
        with open('snp-positions.json', 'r') as f_in:
            snp_positions = json.load(f_in) #get_variant_positions(reference_id, table='snp')
        with open('indel-positions.json', 'r') as f_in:
            indel_positions = json.load(f_in) #get_variant_positions(reference_id, table='indel')

        for sample_id, sample in samples.items():
            # Parse through variants for each sample
            variants = get_variants(sample_id, snp_positions, indel_positions,
                                    reference_id, user.pk)
            alternate_genome = generate_alternate_genome(
                variants, reference, sample['name']
            )

            # Get kmers of the variants
            total_kmers = {}
            for position, vals in alternate_genome.items():
                kmers, is_cluster = self.build_kmer(alternate_genome, position)
                alternate_genome[position]['is_variant_cluster'] = is_cluster
                alternate_genome[position]['kmers'] = kmers
                for kmer in kmers:
                    if kmer == "SNP/InDel Overlap":
                        total_kmers[kmer] = "NOT_FOUND"
                    else:
                        total_kmers[kmer] = "NOT_FOUND"
                        total_kmers[reverse_complement(kmer)] = "NOT_FOUND"

            # verify kmers against jellyfish counts
            jf_database = "{0}/{1}/{2}/{2}/analyses/kmer/{2}.jf".format(
                opts['staphopia'],
                sample['name'][0:6],
                sample['name']
            )
            kmer_counts = self.verify_kmers(total_kmers, jf_database)
            self.print_summary(
                sample, alternate_genome, kmer_counts, summary, annotations,
                print_all=opts['printall'], skip_kmers=opts['nokmers']
            )

    @timeit
    def print_summary(self, sample, alternate_genome, kmer_counts, summary,
                      annotation, print_all=False, skip_kmers=False):
        # Print the results
        cols = ['sample_id', 'position', 'has_zero_count', 'reference',
                'alternate', 'is_variant', 'is_snp', 'is_insertion',
                'is_variant_cluster', 'is_genic', 'annotation_id',
                'coverage', 'genotype_quality', 'qual_by_depth',
                'raw_quality', 'variant_kmer', 'jf_counts',
                'total_jf_count']
        genome = []
        annotation_sequence = OrderedDict()
        results = OrderedDict()
        with open(f'extract-genome/{sample["name"]}-details.txt', 'w') as fh:
            fh.write("\t".join(cols))
            fh.write("\n")
            for position, base in alternate_genome.items():
                genome.append(base['alternate_base'])
                annotation_id = int(base['annotation_id'])
                if annotation_id not in annotation_sequence:
                    annotation_sequence[annotation_id] = OrderedDict()

                annotation_sequence[annotation_id][position] = base['alternate_base']
                if annotation_id not in results:
                    results[annotation_id] = {
                        'annotation_id': annotation_id,
                        'has_zero_count': False,
                        'total_snps': 0,
                        'total_indels': 0,
                        'total_variants': 0
                    }

                if annotation_id in summary:
                    if base['is_variant']:
                        results[annotation_id]['total_variants'] += 1
                        if base['is_snp']:
                            results[annotation_id]['total_snps'] += 1
                        else:
                            results[annotation_id]['total_indels'] += 1
                    counts, total, has_zero_count = self.process_kmers(
                        base['kmers'], kmer_counts
                    )
                    if has_zero_count:
                        if not results[annotation_id]['has_zero_count']:
                            results[annotation_id]['has_zero_count'] = True
                    kmers = ",".join(base['kmers'])
                    if skip_kmers:
                        kmers = "-"
                    fh.write('\t'.join([str(s) for s in [
                        sample['sample_id'],
                        position,
                        has_zero_count,
                        base['reference_base'],
                        base['alternate_base'],
                        base['is_variant'],
                        base['is_snp'],
                        base['is_insertion'],
                        base['is_variant_cluster'],
                        True if annotation_id > 1 else False,
                        annotation_id,
                        base['DP'],
                        base['GQ'],
                        base['QD'],
                        base['quality'],
                        kmers,
                        ",".join(counts),
                        total
                    ]]))
                    fh.write("\n")
                elif print_all:
                    counts, total, has_zero_count = self.process_kmers(
                        base['kmers'], kmer_counts
                    )
                    if has_zero_count:
                        if not results[annotation_id]['has_zero_count']:
                            results[annotation_id]['has_zero_count'] = True
                    kmers = ",".join(alternate_genome[position]['kmers'])
                    if skip_kmers:
                        kmers = "-"
                    fh.write('\t'.join([str(s) for s in [
                        sample['sample_id'],
                        position,
                        has_zero_count,
                        base['reference_base'],
                        base['alternate_base'],
                        base['is_variant'],
                        False,
                        False,
                        False,
                        True if annotation_id > 1 else False,
                        annotation_id,
                        0,
                        0,
                        0,
                        0,
                        kmers,
                        ",".join(counts),
                        total
                    ]]))
                    fh.write("\n")

        with open(f'extract-genome/{sample["name"]}-genome.fasta', 'w') as fh:
            genome = ''.join(genome)
            header = ">{0}|{1}|length={2}".format(
                sample["sample_id"],
                sample["name"],
                len(genome)
            )
            fh.write(f'{header}\n')
            for line in [genome[i:i+80] for i in range(0, len(genome), 80)]:
                fh.write(f'{line}\n')

        cols = ['sample_id', 'annotation_id', 'has_zero_count', 'total_snps',
                'total_indels', 'total_variants']
        with open(f'extract-genome/{sample["name"]}-annotation-details.txt', 'w') as fh:
            fh.write("\t".join(cols))
            fh.write("\n")
            for annotation_id, vals in results.items():
                if print_all or annotation_id in summary:
                    fh.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(
                        sample['sample_id'],
                        annotation_id,
                        vals['has_zero_count'],
                        vals['total_snps'],
                        vals['total_indels'],
                        vals['total_variants']
                    ))

        with open(f'extract-genome/{sample["name"]}-annotation.fasta', 'w') as fh:
            for annotation_id, vals in annotation_sequence.items():
                # Ignore intergenic regions
                if annotation_id > 1:
                    if print_all or annotation_id in summary:
                        gene = []
                        positions = []
                        for position, base in vals.items():
                            gene.append(base)
                            positions.append(position)

                        if (min(positions) == annotation[annotation_id]['start'] and
                                max(positions) == annotation[annotation_id]['end']):
                            gene = ''.join(gene)
                            header = ">{0}|{1}|{2}|{3}|length={4}".format(
                                sample["sample_id"],
                                sample["name"],
                                annotation_id,
                                annotation[annotation_id]['locus_tag'],
                                len(gene)
                            )
                            fh.write(f'{header}\n')
                            for line in [gene[i:i+80]
                                         for i in range(0, len(gene), 80)]:
                                fh.write(f'{line}\n')

        return results

    def process_kmers(self, kmers, kmer_counts):
        """Assess the counts for each kmer."""
        counts = []
        total = 0
        has_zero_count = False
        for kmer in kmers:
            count = kmer_counts[kmer]
            counts.append(str(count))
            if count != "NOT_FOUND":
                total += count
                if count == 0:
                    has_zero_count = True

        return [counts, total, has_zero_count]

    def build_kmer(self, alternate_genome, position, length=15):
        """Build kmer with variant at center."""
        is_variant_cluster = False

        start, start_cluster = self.build_start_seqeunce(
            alternate_genome, position - 1, length
        )
        end, end_cluster = self.build_end_sequence(
            alternate_genome, position + 1, length
        )

        if start_cluster or end_cluster:
            is_variant_cluster = True

        if alternate_genome[position]['alternate_base'] == "-":
            return [['SNP/InDel Overlap'], is_variant_cluster]

        kmer = '{0}{1}{2}'.format(
            start,
            alternate_genome[position]['alternate_base'],
            end
        )
        total = length + length + 1
        if len(kmer) > total:
            # Insertions
            kmer = ["".join(i) for i in self.split_into_kmers(kmer, total)]
        elif len(kmer) < total:
            raise CommandError(
                ('Kmer is less than the expected length of {0}'
                 '. position: {1} ... kmer: {2}').format(total, position, kmer)
            )
        else:
            kmer = [kmer]

        return [kmer, is_variant_cluster]

    @timeit
    def verify_kmers(self, kmers, jf):
        """Get count of kmer via jellyfish."""
        jf_output = None
        with tempfile.NamedTemporaryFile() as temp:
            for kmer in kmers.keys():
                if kmer.startswith('SNP/InDel'):
                    pass
                else:
                    temp.write('>{0}\n{0}\n'.format(kmer).encode())
            temp.flush()
            jf_output = jf_query(jf, temp.name)

        for line in jf_output.split('\n'):
            if not line:
                continue
            kmer, count = line.rstrip().split(' ')
            count = int(count)
            kmers[reverse_complement(kmer)] = count
            kmers[kmer] = count
        return kmers

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

    def build_start_seqeunce(self, alternate_genome, position, length):
        seq = []
        is_variant_cluster = False
        if position == 0:
            position = len(alternate_genome)

        while len(seq) < length:
            base = alternate_genome[position]['alternate_base']
            if alternate_genome[position]['is_variant']:
                is_variant_cluster = True

            if base != '-':
                seq.append(base)
            position -= 1

            if position == 0:
                position = len(alternate_genome)

        seq.reverse()
        return ["".join(seq), is_variant_cluster]

    def build_end_sequence(self, alternate_genome, position, length):
        seq = []
        is_variant_cluster = False
        if position > len(alternate_genome):
            position = 1

        while len(seq) < length:
            base = alternate_genome[position]['alternate_base']
            if alternate_genome[position]['is_variant']:
                is_variant_cluster = True

            if base != '-':
                seq.append(base)
            position += 1

            if position > len(alternate_genome):
                position = 1

        return ["".join(seq), is_variant_cluster]
