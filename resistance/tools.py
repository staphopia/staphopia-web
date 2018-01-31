"""
Useful functions associated with resistance.

To use:
from resistance.tools import UTIL1, UTIL2, etc...
"""
import numpy

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, timeit
from resistance.models import Ariba, AribaSequence, Cluster, ResistanceClass


@timeit
@transaction.atomic
def insert_resistance(sample, version, files, force=False):
    """Insert the Ariba resistance results to the database."""
    if force:
        delete_resistance(sample, version)

    results, sequences = read_report(files)

    try:
        Ariba.objects.create(sample=sample, version=version, results=results)
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Ariba Resistance: Insert error for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))

    try:
        AribaSequence.objects.create(
            sample=sample, version=version, sequences=sequences
        )
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Ariba Resistance: Insert error for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))


def get_clusters():
    """Get clusters."""
    cluster = {}
    for row in Cluster.objects.all():
        cluster[row.name] = row
    return cluster


@transaction.atomic
def create_cluster(cluster):
    return Cluster.objects.create(
        name=cluster['cluster'],
        resistance_class=cluster['resistance_class'],
        mechanism=cluster['mechanism'],
        ref_name=cluster['ref_name'],
        database=cluster['database'],
        headers=cluster['headers']
    )


def get_resistance_class():
    """Get Resitance classes."""
    resistance_class = {}
    for row in ResistanceClass.objects.all():
        resistance_class[row.name] = row
    return resistance_class


@transaction.atomic
def create_resistance_class(name):
    """Insert a new resistance class."""
    return ResistanceClass.objects.create(name=name)


@timeit
def read_report(files):
    """
    Convert the Ariba report to JSON.

    See: https://github.com/sanger-pathogens/ariba/wiki/Task:-run#report-file
    """
    resistance_class = get_resistance_class()
    clusters = get_clusters()
    fasta = read_fasta(files['resistance_assembled_seqs'], compressed=True)
    results = []
    sequences = {}
    total = 1
    with open(files["resistance_report"], 'r') as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith("#"):
                cols = line.split('\t')
            else:
                row = dict(zip(cols, line.split('\t')))
                text = row['free_text'].replace('; ', ';')
                text = dict(s.split(':') for s in text.split(';'))
                if row['cluster'] not in clusters:
                    clusters[row['cluster']] = create_cluster({
                        'cluster': row['cluster'],
                        'resistance_class': text['class'],
                        'mechanism': text['mechanism'],
                        'ref_name': row['ref_name'],
                        'database': text['Source_Database'],
                        'headers': text['Source_Headers']
                    })

                seq = None
                for key in fasta.keys():
                    if key.startswith(row['ref_name']):
                        seq = fasta[key]

                if text['class'] not in resistance_class:
                    resistance_class[text['class']] = create_resistance_class(
                        name=text['class']
                    )

                results.append({
                    'id': total,
                    'cluster': clusters[row['cluster']].pk,
                    'class': resistance_class[text['class']].pk,
                    'gene': row['gene'],
                    'var_only': row['var_only'],
                    'flag': row['flag'],
                    'reads': row['reads'],
                    'ref_len': row['ref_len'],
                    'ref_base_assembled': row['ref_base_assembled'],
                    'pc_ident': row['pc_ident'],
                    'ctg_len': row['ctg_len'],
                    'ctg_cov': row['ctg_cov'],
                    'known_var': row['known_var'],
                    'var_type': row['var_type'],
                    'var_seq_type': row['var_seq_type'],
                    'known_var_change': row['known_var_change'],
                    'has_known_var': row['has_known_var'],
                    'ref_ctg_change': row['ref_ctg_change'],
                    'ref_ctg_effect': row['ref_ctg_effect'],
                    'ref_start': row['ref_start'],
                    'ref_end': row['ref_end'],
                    'ref_nt': row['ref_nt'],
                    'ctg_start': row['ctg_start'],
                    'ctg_end': row['ctg_end'],
                    'ctg_nt': row['ctg_nt'],
                    'smtls_total_depth': row['smtls_total_depth'],
                    'smtls_nts': row['smtls_nts'],
                    'smtls_nts_depth': row['smtls_nts_depth'],
                    'var_description': row['var_description'],
                })
                sequences[total] = {
                    'id': total,
                    'cluster': clusters[row['cluster']].pk,
                    'class': resistance_class[text['class']].pk,
                    'dna': seq
                }
                total += 1

    return [results, sequences]


def delete_resistance(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Ariba.objects.filter(sample=sample, version=version).delete()
    AribaSequence.objects.filter(sample=sample, version=version).delete()
