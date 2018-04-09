"""
Useful functions associated with resistance.

To use:
from resistance.tools import UTIL1, UTIL2, etc...
"""
from collections import OrderedDict
import numpy
import sys

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

    resistance_class = get_resistance_class()
    clusters = get_clusters()
    results, sequences = read_report(files, resistance_class, clusters)
    summary = read_summary(files, clusters)

    try:
        Ariba.objects.create(sample=sample, version=version, results=results,
                             summary=summary)
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
def read_report(files, resistance_class, clusters):
    """
    Convert the Ariba report to JSON.

    See: https://github.com/sanger-pathogens/ariba/wiki/Task:-run#report-file
    """
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
                temp = {}
                for s in text.split(';'):
                    if ':' in s:
                        key, val = s.split(':')
                        temp[key] = val
                    else:
                        print(f'Free Text {s}: {files["resistance_report"]}',
                              file=sys.stderr)
                text = temp
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
                    'cluster_id': clusters[row['cluster']].pk,
                    'cluster': row['cluster'],
                    'resistance_class': text['class'],
                    'resistance_class_id': resistance_class[text['class']].pk,
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
                    'cluster_id': clusters[row['cluster']].pk,
                    'resistance_class_id': resistance_class[text['class']].pk,
                    'dna': seq
                }
                total += 1

    return [results, sequences]


@timeit
def read_summary(files, clusters):
    """Ariba summary report."""
    hits = OrderedDict()
    first_line = True
    with open(files["resistance_summary"], 'r') as fh:
        cols = None
        for line in fh:
            line = line.rstrip()
            if first_line:
                cols = line.split(',')
                first_line = False
            else:
                row = dict(zip(cols, line.split(',')))
                for key, val in row.items():
                    if key != 'name':
                        cluster, field = key.split('.')
                        if cluster not in hits:
                            hits[cluster] = {
                                'cluster_id': clusters[cluster].pk,
                                'cluster': cluster,
                                'resistance_class': (
                                    clusters[cluster].resistance_class
                                )
                            }
                        hits[cluster][field] = val

    summary = []
    for key, val in hits.items():
        summary.append(val)
    return summary


def delete_resistance(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Ariba.objects.filter(sample=sample, version=version).delete()
    AribaSequence.objects.filter(sample=sample, version=version).delete()
