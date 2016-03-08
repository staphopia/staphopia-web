"""
Useful functions associated with sequence.

To use:
from sequence.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_json

from sequence.models import Quality


@transaction.atomic
def insert_sequence_stats(stats, sample, is_original=False):
    """Insert seqeunce quality metrics into database."""
    json_data = read_json(stats)
    try:
        table_object = Quality(
            sample=sample,
            is_original=is_original,
            rank=__get_rank(json_data),
            **json_data
        )
        table_object.save()
        print('Sequence quality stats saved.')
        return True
    except IntegrityError as e:
        raise CommandError(
            'An error occured when inserting stats. Error {0}'.format(e)
        )


def __get_rank(self, data):
        """
        Determine the rank of the reads.

        3: Gold, 2: Silver, 1: Bronze
        """
        if data['mean_read_length'] >= 95:
            if data['coverage'] >= 45 and data['qual_mean'] >= 30:
                return 3
            elif data['coverage'] >= 20 and data['qual_mean'] >= 20:
                return 2
            else:
                return 1
        else:
            return 1
