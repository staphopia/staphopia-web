"""
Useful functions associated with sequence.

To use:
from sequence.tools import UTIL1, UTIL2, etc...
"""
import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_json, timeit

from sequence.models import Stat


@transaction.atomic
def insert_fastq_stats(stats, sample, is_original=False, force=False):
    """Insert seqeunce quality metrics into database."""
    json_data = read_json(stats)
    if force:
        delete_stats(sample, is_original)
    insert_sequence_stats(json_data["qc_stats"], json_data["read_lengths"],
                          json_data["per_base_quality"], sample, is_original)


@transaction.atomic
def delete_stats(sample, is_original):
    """Force update, so remove from table."""
    print("\tForce used, emptying FASTQ related results.")
    Stat.objects.filter(sample=sample, is_original=is_original).delete()


@timeit
@transaction.atomic
def insert_sequence_stats(stats, read_lengths, qual_per_base, sample,
                          is_original=False):
    """Insert sequence quality metrics into database."""
    try:
        Stat.objects.create(
            sample=sample,
            is_original=is_original,
            rank=__get_rank(stats),
            read_lengths=json.dumps(read_lengths, sort_keys=True),
            qual_per_base=json.dumps(qual_per_base, sort_keys=True),
            **stats
        )
    except IntegrityError as e:
        raise CommandError(
            'An error occured when inserting stats. Error {0}'.format(e)
        )


def __get_rank(data):
    """
    Determine the rank of the reads.

    3: Gold, 2: Silver, 1: Bronze
    """
    if data['read_mean'] >= 95:
        if data['coverage'] >= 100 and data['qual_mean'] >= 30:
            return 3
        elif data['coverage'] >= 20 and data['qual_mean'] >= 20:
            return 2
        else:
            return 1
    else:
        return 1
