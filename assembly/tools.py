"""
Useful functions associated with assembly.

To use:
from assembly.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_json

from assembly.models import Stats


@transaction.atomic
def insert_assembly_stats(assembly, sample, is_scaffolds=False):
    """Insert assembly statistics for a given sample."""
    json_data = read_json(assembly)
    try:
        assembly = Stats(
            sample=sample,
            is_scaffolds=is_scaffolds,
            **json_data
        )
        assembly.save()
        return True
    except IntegrityError as e:
        raise CommandError(
            'An error occured when inserting assembly. Error {0}'.format(e)
        )
