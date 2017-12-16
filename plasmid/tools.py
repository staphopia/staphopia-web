"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, read_json, timeit

from plasmid.models import Contig, Summary


@timeit
@transaction.atomic
def insert_plasmid_stats(sample, version, files, force=False):
    """Insert plasmid assembly statistics for a given sample."""
    if force:
        delete_stats(sample, version)

    if files['plasmid_contig_stats']:
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
def insert_plasmid_assembly(assembly, sample, is_plasmids=False, force=False,
                            skip=False):
    """Insert the assembled scaffolds to the database."""
    save = True
    if force:
        print("\tForce used, emptying Assembly sequence related results.")
        Contig.objects.filter(sample=sample, is_plasmids=is_plasmids).delete()
    elif skip:
        try:
            Contig.objects.get(sample=sample, is_plasmids=is_plasmids)
            # Single contig/plasmid
            print("\tSkip reloading existing Assembly Contigs.")
            save = False
        except Contig.MultipleObjectsReturned:
            # Multiple contigs
            print("\tSkip reloading existing Assembly Contigs.")
            save = False
        except Contig.DoesNotExist:
            pass

    if save:
        assembly = read_fasta(assembly, compressed=True)
        contigs = []
        for name, seq in assembly.items():
            contigs.append(Contig(
                sample=sample,
                name=name,
                sequence=seq
            ))

        try:
            Contig.objects.bulk_create(contigs, batch_size=100)
            print('\tAssembly sequences saved.')
        except IntegrityError as e:
            raise CommandError('{0} Assembly Contigs Error: {1}'.format(
                sample.sample_tag, e)
            )


def get_contig(sample, name):
    """return a contig instance."""
    try:
        return Contig.objects.get(sample=sample, is_plasmids=False, name=name)
    except Contig.DoesNotExist:
        return Contig.objects.get(name="none")
