"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, read_json, timeit

from assembly.models import Contig, Summary


@timeit
@transaction.atomic
def insert_assembly_stats(assembly, sample, is_scaffolds=False, force=False,
                          is_plasmids=False, skip=False):
    """Insert assembly statistics for a given sample."""
    json_data = read_json(assembly)
    try:
        save = True
        if force:
            print("\tForce used, emptying Assembly related results.")
            Summary.objects.filter(sample=sample).delete()
        elif skip:
            try:
                Summary.objects.get(sample=sample)
                print("\tSkip reloading existing Assembly Summary.")
                save = False
            except Summary.DoesNotExist:
                pass

        if save:
            assembly = Summary(sample=sample, **json_data)
            assembly.save()
        return True
    except IntegrityError as e:
        raise CommandError(
            'An error occured when inserting assembly. Error {0}'.format(e)
        )


@timeit
@transaction.atomic
def insert_assembly(assembly, sample, is_plasmids=False, force=False,
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
