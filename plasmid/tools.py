"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, read_json, timeit

from plasmid.models import Contig, Sequence, Summary


@timeit
@transaction.atomic
def insert_plasmid_stats(sample, version, files, force=False):
    """Insert plasmid assembly statistics for a given sample."""
    if force:
        delete_stats(sample, version)

    if files['plasmid']:
        try:
            json_data = read_json(files['plasmid_contig_stats'])
            Summary.objects.create(sample=sample, version=version, **json_data)
        except IntegrityError as e:
            raise CommandError(' '.join([
                f'Unable to insert stats for {sample.name} ({sample.id}).',
                f'Please use --force to update stats. Error: {e}'
            ]))
    else:
        print(f'{sample.name} does not have a plasmid assembly, skipping.')


@transaction.atomic
def delete_stats(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Summary.objects.filter(sample=sample, version=version).delete()


@timeit
@transaction.atomic
def insert_plasmid_contigs(sample, version, files, force=False):
    """Insert the assembled scaffolds to the database."""
    if force:
        delete_contigs(sample, version)

    if files['plasmid']:
        assembly = read_fasta(files['plasmid_contigs'], compressed=True)
        graph = read_fasta(files['plasmid_graph'], compressed=True)

        fasta = {}
        contig_objects = []
        for spades, sequence in assembly.items():
            # Example SPAdes name: NODE_37_length_341_cov_381.897727
            cols = spades.split('_')
            staphopia = ''.join([
                f'{sample.id}|{sample.name}|{cols[1]}|plasmid ',
                f'coverage={cols[5]} length={cols[3]} ',
                f'analysis_version={version.tag}'
            ])

            # Update FASTA entry, and create Contig object
            fasta[staphopia] = sequence
            contig_objects.append(Contig(
                sample=sample,
                version=version,
                spades=spades,
                staphopia=staphopia
            ))
        try:
            Contig.objects.bulk_create(contig_objects, batch_size=500)
            print(f'{sample.name}: Plasmid contig names saved.')
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
    else:
        print(f'{sample.name} does not have a plasmid assembly, skipping.')


def delete_contigs(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying assembly related results.')
    Contig.objects.filter(sample=sample, version=version).delete()
    Sequence.objects.filter(sample=sample, version=version).delete()
