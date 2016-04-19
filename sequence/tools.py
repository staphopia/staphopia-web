"""
Useful functions associated with sequence.

To use:
from sequence.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_json

from sequence.models import Stat, Length, Quality


@transaction.atomic
def insert_fastq_stats(stats, sample, is_original=False, force=False):
    """Insert seqeunce quality metrics into database."""
    json_data = read_json(stats)
    if force:
        delete_stats(sample, is_original)
    insert_sequence_stats(json_data["qc_stats"], sample, is_original)
    insert_read_lengths(json_data["read_lengths"], sample, is_original)
    insert_per_base_quality(json_data["per_base_quality"], sample, is_original)


@transaction.atomic
def delete_stats(sample, is_original):
    """Force update, so remove from table."""
    print("\t\tForce used, emptying FASTQ related tables.")
    Stat.objects.filter(sample=sample, is_original=is_original).delete()
    Length.objects.filter(sample=sample, is_original=is_original).delete()
    Quality.objects.filter(sample=sample, is_original=is_original).delete()


@transaction.atomic
def insert_sequence_stats(stats, sample, is_original=False):
    """Insert sequence quality metrics into database."""
    try:
        Stat.objects.create(
            sample=sample,
            is_original=is_original,
            rank=__get_rank(stats),
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
        if data['coverage'] >= 50 and data['qual_mean'] >= 30:
            return 3
        elif data['coverage'] >= 20 and data['qual_mean'] >= 20:
            return 2
        else:
            return 1
    else:
        return 1


@transaction.atomic
def insert_read_lengths(stats, sample, is_original=False):
    """Insert read lengths into database."""
    try:
        counts = []
        for length, count in sorted(stats.items()):
            counts.append(Length(
                sample=sample,
                is_original=is_original,
                length=length,
                count=count
            ))

        Length.objects.bulk_create(counts)
    except IntegrityError as e:
        raise CommandError(
            'An error occured when inserting read lengths. Error {0}'.format(e)
        )


@transaction.atomic
def insert_per_base_quality(stats, sample, is_original=False):
    """Insert per base quality into database."""
    try:
        positions = []
        for position, quality in sorted(stats.items()):
            positions.append(Quality(
                sample=sample,
                is_original=is_original,
                position=position,
                quality=quality
            ))

        Quality.objects.bulk_create(positions)
    except IntegrityError as e:
        raise CommandError(
            ('An error occured when inserting per base quality.'
             ' Error {0}').format(e)
        )
