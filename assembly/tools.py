"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_fasta, read_json, timeit

from assembly.models import Contigs, Stats


@timeit
@transaction.atomic
def insert_assembly_stats(assembly, sample, is_scaffolds=False, force=False,
                          is_plasmids=False, skip=False):
    """Insert assembly statistics for a given sample."""
    json_data = read_json(assembly)
    try:
        save = True
        if force:
            print("\tForce used, emptying Assembly stats related results.")
            Stats.objects.filter(
                sample=sample,
                is_scaffolds=is_scaffolds,
                is_plasmids=is_plasmids
            ).delete()
        elif skip:
            try:
                Stats.objects.get(sample=sample, is_scaffolds=is_scaffolds,
                                  is_plasmids=is_plasmids)
                print("\tSkip reloading existing Assembly Stats.")
                save = False
            except Stats.DoesNotExist:
                pass

        if save:
            assembly = Stats(
                sample=sample,
                is_scaffolds=is_scaffolds,
                is_plasmids=is_plasmids,
                **json_data
            )
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
        Contigs.objects.filter(sample=sample, is_plasmids=is_plasmids).delete()
    elif skip:
        try:
            Contigs.objects.get(sample=sample, is_plasmids=is_plasmids)
        except Contigs.MultipleObjectsReturned:
            print("\tSkip reloading existing Assembly Contigs.")
            save = False
        except Contigs.DoesNotExist:
            pass

    if save:
        assembly = read_fasta(assembly, compressed=True)
        contigs = []
        for name, seq in assembly.items():
            contigs.append(Contigs(
                sample=sample,
                is_plasmids=is_plasmids,
                name=name,
                sequence=seq
            ))

        try:
            Contigs.objects.bulk_create(contigs, batch_size=100)
            print('\tAssembly sequences saved.')
        except IntegrityError as e:
            raise CommandError('{0} Assembly Contigs Error: {1}'.format(
                sample.sample_tag, e)
            )


def get_contig(sample, name):
    """return a contig instance."""
    try:
        return Contigs.objects.get(sample=sample, is_plasmids=False, name=name)
    except Contigs.DoesNotExist:
        return Contigs.objects.get(name="none")
