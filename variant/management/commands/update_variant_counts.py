"""Update members of SNP and InDel IDs."""
from collections import OrderedDict
import sys

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from api.utils import query_database
from staphopia.utils import timeit
from variant.models import Reference, Counts


@timeit
def get_annotation(reference_id):
    sql = """SELECT DISTINCT(reference_position), annotation_id
             FROM variant_snp
             WHERE reference_id={0}
             ORDER BY reference_position;""".format(
        reference_id
    )
    annotation = {}
    for row in query_database(sql):
        annotation[row['reference_position']] = row['annotation_id']
    return annotation


class Command(BaseCommand):
    """Update members of SNP and InDel IDs."""

    help = 'Update members of SNP and InDel IDs.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('counts', metavar='VARIANT_COUNTS',
                            help=('Text file of variant counts by position.'))
        parser.add_argument('--reference', metavar='REFERENCE',
                            default='gi|29165615|ref|NC_002745.2|',
                            help=('Reference genome.'))
        parser.add_argument('--is_unique', action='store_true',
                            help='Counts reflect the unique set.')

    def handle(self, *args, **opts):
        """Insert results to database."""
        try:
            reference = Reference.objects.get(name=opts['reference'])
        except IntegrityError as e:
            raise CommandError(f'Reference Error: {e}')

        # Full update, so empty tables
        self.delete_members(reference, is_unique=opts['is_unique'])

        # Get Annotation ID by Position
        annotation = get_annotation(reference.pk)
        counts = []
        i = 1

        print('Start variant reading/processing')
        with open(opts['counts'], 'r') as fh:
            for line in fh:
                if line.startswith('position'):
                    pass
                else:
                    """
                    cols[0] = position
                    cols[1] = indel
                    cols[2] = nongenic_indel
                    cols[3] = nongenic_snp
                    cols[4] = nonsyn
                    cols[5] = syn
                    cols[6] = total
                    """
                    if i % 100000 == 0:
                        print(f'{i} positions processed')
                    line = line.rstrip()
                    cols = [int(i) for i in line.split('\t')]
                    counts.append(Counts(
                        reference_id=reference.pk,
                        annotation_id=annotation[cols[0]],
                        position=cols[0],
                        is_mlst_set=opts['is_unique'],
                        nongenic_indel=cols[2],
                        nongenic_snp=cols[3],
                        indel=cols[1],
                        synonymous=cols[5],
                        nonsynonymous=cols[4],
                        total=cols[6]
                    ))
                    i += 1

        # Update member columns
        self.insert_counts(counts)

    @timeit
    @transaction.atomic
    def delete_members(self, reference, is_unique=False):
        """Force update, so remove from table."""
        print('Emptying member related results.')
        Counts.objects.filter(
            reference=reference, is_mlst_set=is_unique
        ).delete()


    @timeit
    @transaction.atomic
    def insert_counts(self, counts):
        """Bulk insert snp members."""
        print(f'Inserting variants counts...')
        Counts.objects.bulk_create(counts, batch_size=100000)
