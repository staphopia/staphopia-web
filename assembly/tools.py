"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, read_json, timeit
from assembly.models import Contig, Sequence, Summary


@timeit
@transaction.atomic
def insert_assembly_stats(sample, version, files, force=False):
    """Insert assembly statistics for a given sample."""
    if force:
        delete_stats(sample, version)

    try:
        json_data = read_json(files['assembly_contig_stats'])
        Summary.objects.create(sample=sample, version=version, **json_data)
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Unable to insert stats for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))


@transaction.atomic
def delete_stats(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Summary.objects.filter(sample=sample, version=version).delete()


@timeit
@transaction.atomic
def insert_assembly_contigs(sample, version, files, force=False):
    """Insert the assembled scaffolds to the database."""
    if force:
        delete_contigs(sample, version)

    assembly = read_fasta(files['assembly_contigs'], compressed=True)
    graph = read_fasta(files['assembly_graph'], compressed=True)

    # Get the PROKKA naming of contigs
    prokka_name = {}
    with open(files['annotation_contigs'], 'r') as fh:
        for line in fh:
            spades, prokka = line.rstrip().split('\t')
            prokka_name[spades] = prokka

    fasta = {}
    contig_objects = []
    for spades, sequence in assembly.items():
        # Example SPAdes name: NODE_37_length_341_cov_381.897727
        cols = spades.split('_')
        staphopia = ''.join([
            f'{sample.id}|{sample.name}|{cols[1]} coverage={cols[5]} ',
            f'length={cols[3]} analysis_version={version.tag}'
        ])

        # Update FASTA entry, and create Contig object
        fasta[staphopia] = sequence
        prokka = '-'
        if spades in prokka_name:
            prokka = prokka_name[spades]

        contig_objects.append(Contig(
            sample=sample,
            version=version,
            spades=spades,
            prokka=prokka,
            staphopia=staphopia
        ))

    try:
        Contig.objects.bulk_create(contig_objects, batch_size=500)
        print(f'{sample.name}: Assembled contig names saved.')
    except IntegrityError as e:
        raise CommandError(f'{sample.name} Contig Name Error: {e}')

    try:
        Sequence.objects.create(
            sample=sample,
            version=version,
            fasta=fasta,
            graph=graph
        )
    except IntegrityError as e:
        raise CommandError(f'{sample.name} Fasta save error: {e}')


def delete_contigs(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Contig.objects.filter(sample=sample, version=version).delete()
    Sequence.objects.filter(sample=sample, version=version).delete()


def get_contig(sample, name):
    """return a contig instance."""
    try:
        return Contig.objects.get(sample=sample, is_plasmids=False, name=name)
    except Contig.DoesNotExist:
        return Contig.objects.get(name="none")
