"""Flag Public Samples that fail some criteria."""
from collections import OrderedDict
from django.db import connection
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from api.utils import query_database
from api.queries.assemblies import get_assembly_stats
from api.queries.samples import get_public_samples
from api.queries.sequence_types import (
    get_sequence_type,
    get_mlst_blast_results
)
from api.queries.sequences import get_sequencing_stats
from sample.models import Sample, Flag


def clear_flags(sample_id, user_id):
    cursor = connection.cursor()
    sql = """UPDATE sample_sample
             SET is_flagged = FALSE
             WHERE user_id={0}""".format(user_id)
    cursor.execute(sql)

    sql = """DELETE FROM sample_flag WHERE sample_id IN ({0})""".format(
        ','.join([str(i) for i in sample_id]),
    )
    cursor.execute(sql)


def get_mlst(sample_ids, user):
    samples = {}
    for row in get_sequence_type(sample_ids, user):
        samples[row['sample_id']] = row
    return samples


def get_sequence_stats(sample_ids, user_id):
    samples = {}
    for row in get_sequencing_stats(sample_ids, user_id, stage='cleanup'):
        samples[row['sample_id']] = row['coverage']
    return samples


def get_assembly(sample_ids, user_id):
    samples = {}
    for row in get_assembly_stats(sample_ids, user_id):
        samples[row['sample_id']] = row
    return samples


def get_annotation():
    samples = {}
    sql = 'SELECT sample_id FROM annotation_annotation;'
    for row in query_database(sql):
        samples[row['sample_id']] = True
    return samples


def get_variant():
    samples = {}
    for row in query_database('SELECT sample_id FROM variant_variant;'):
        samples[row['sample_id']] = True
    return samples


def get_cgmlst():
    samples = {}
    for row in query_database('SELECT sample_id FROM cgmlst_cgmlst;'):
        samples[row['sample_id']] = True
    return samples


def get_sccmec():
    samples = {}
    for row in query_database('SELECT sample_id FROM sccmec_primers;'):
        samples[row['sample_id']] = 1

    for row in query_database('SELECT sample_id FROM sccmec_subtypes;'):
        if row['sample_id'] not in samples:
            samples[row['sample_id']] = 1
        else:
            samples[row['sample_id']] += 1

    for row in query_database('SELECT sample_id FROM sccmec_proteins;'):
        if row['sample_id'] not in samples:
            samples[row['sample_id']] = 1
        else:
            samples[row['sample_id']] += 1

    for row in query_database('SELECT sample_id FROM sccmec_coverage;'):
        if row['sample_id'] not in samples:
            samples[row['sample_id']] = 1
        else:
            samples[row['sample_id']] += 1

    return samples


def get_mlst_blast(sample_ids, user):
    samples = {}
    for row in get_mlst_blast_results(sample_ids, user):
        samples[row['sample_id']] = row['unassigned']

    return samples


class Command(BaseCommand):
    """Flag Public Samples that fail some criteria."""

    help = 'Flag Public Samples that fail some criteria.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--debug', action='store_true',
                            help='Do not write to the database.')

    def handle(self, *args, **opts):
        """Verify an analysis completed."""
        # Validate all files are present
        user = User.objects.get(username='ena')
        counts = {
            'low_cov': {'sample': [], 'reason': 'coverage < 20x'},
            'missing_assembly': {
                'sample': [], 'reason': 'missing assembly results'
            },
            'missing_annotation': {
                'sample': [], 'reason': 'missing annotation results'
            },
            'missing_qc': {
                'sample': [], 'reason': 'missing sequence qc results'
            },
            'missing_variants': {
                'sample': [], 'reason': 'missing variant results'
            },
            'missing_mlst': {
                'sample': [], 'reason': 'missing mlst results'
            },
            'missing_sccmec': {
                'sample': [], 'reason': 'missing sccmec results'
            },
            'missing_cgmlst': {
                'sample': [], 'reason': 'missing cgmlst results'
            },
            'mlst_unassigned': {
                'sample': [], 'reason': 'zero mlst loci assigned an allele'
            },
            'assembly_size': {
                'sample': [],
                'reason': 'unexpected assembled size (<1.8mb or >3.8mb)'
            },
            'gc_content': {
                'sample': [],
                'reason': "unexpected GC content (<28% or >38%)"
            },
        }
        samples = get_public_samples()
        sample_ids = [s['sample_id'] for s in samples]
        if not opts['debug']:
            # Reset flagged status for all samples
            clear_flags(sample_ids, user.pk)
        assembly = get_assembly(sample_ids, user.pk)
        mlst = get_mlst(sample_ids, user)
        sequence_stats = get_sequence_stats(sample_ids, user.pk)
        sccmec = get_sccmec()
        cgmlst = get_cgmlst()
        annotation = get_annotation()
        variant = get_variant()
        mlst_blast = get_mlst_blast(sample_ids, user)
        for sample_id in sample_ids:
            # Flag Missing QC and Low Coverage
            if sample_id not in sequence_stats:
                counts['missing_qc']['sample'].append(sample_id)
            elif sequence_stats[sample_id] < 20:
                counts['low_cov']['sample'].append(sample_id)

            # Flag Incomplete Analysis
            if sample_id not in annotation:
                counts['missing_annotation']['sample'].append(sample_id)

            if sample_id not in sccmec:
                counts['missing_sccmec']['sample'].append(sample_id)

            if sample_id not in cgmlst:
                counts['missing_cgmlst']['sample'].append(sample_id)

            if sample_id not in variant:
                counts['missing_variants']['sample'].append(sample_id)

            if sample_id not in assembly:
                counts['missing_assembly']['sample'].append(sample_id)
            else:
                size = assembly[sample_id]['total_contig_length']
                gc_content = (assembly[sample_id]['contig_percent_g'] +
                              assembly[sample_id]['contig_percent_c'])
                if size <= 1800000 or size >= 3800000:
                    counts['assembly_size']['sample'].append(sample_id)

                if gc_content <= 28 or gc_content >= 38:
                    counts['gc_content']['sample'].append(sample_id)

            if sample_id not in mlst:
                counts['missing_mlst']['sample'].append(sample_id)
            else:
                sequence_type = mlst[sample_id]['st']
                if not sequence_type:
                    if mlst_blast[sample_id] == 7:
                        counts['mlst_unassigned']['sample'].append(sample_id)

        unique = {}
        print('count\treason')
        for key, val in counts.items():
            print(f'{len(val["sample"])}\t{val["reason"]}')
            for sample_id in val["sample"]:
                if not opts['debug']:
                    sample = Sample.objects.get(pk=sample_id)
                    Flag.objects.get_or_create(sample=sample,
                                               reason=val['reason'])
                    sample.is_flagged = True
                    sample.save()
                unique[sample_id] = True

        print(f'\nTotal Samples Flagged: {len(unique)}')
