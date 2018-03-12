"""
Useful functions associated with virulence.

To use:
from virulence.tools import UTIL1, UTIL2, etc...
"""
import numpy

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, timeit
from virulence.models import Ariba, AribaSequence, Cluster


@timeit
@transaction.atomic
def insert_virulence(sample, version, files, force=False):
    """Insert the Ariba virulence results to the database."""
    if force:
        delete_resistance(sample, version)

    results, sequences = read_report(files)

    try:
        Ariba.objects.create(sample=sample, version=version, results=results)
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Ariba Virulence: Insert error for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))

    try:
        AribaSequence.objects.create(
            sample=sample, version=version, sequences=sequences
        )
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Ariba Virulence: Insert error for {sample.name} ({sample.id}).',
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
        ref_name=cluster['ref_name'],
        original_name=cluster['original_name']
    )


@timeit
def read_report(files):
    """
    Convert the Ariba report to JSON.

    See: https://github.com/sanger-pathogens/ariba/wiki/Task:-run#report-file
    """
    clusters = get_clusters()
    fasta = read_fasta(files['virulence_assembled_seqs'], compressed=True)
    results = []
    sequences = {}
    total = 1
    with open(files["virulence_report"], 'r') as fh:
        for line in fh:
            line = line.rstrip()
            if line.startswith("#"):
                cols = line.split('\t')
            else:
                row = dict(zip(cols, line.split('\t')))
                text = row['free_text'].replace('Original name: ', '')
                if row['cluster'] not in clusters:
                    clusters[row['cluster']] = create_cluster({
                        'cluster': row['cluster'],
                        'ref_name': row['ref_name'],
                        'original_name': text,
                    })

                seq = None
                for key in fasta.keys():
                    if key.startswith(row['ref_name']):
                        seq = fasta[key]

                results.append({
                    'id': total,
                    'cluster': clusters[row['cluster']].pk,
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
                    'dna': seq
                }
                total += 1

    return [results, sequences]


@transaction.atomic
def delete_resistance(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying resistance related results.')
    Ariba.objects.filter(sample=sample, version=version).delete()
    AribaSequence.objects.filter(sample=sample, version=version).delete()
