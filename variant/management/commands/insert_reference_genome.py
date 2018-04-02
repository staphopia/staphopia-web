"""Insert Reference genome sequence and annotation IDs"""
from collections import OrderedDict
import sys

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from api.utils import query_database
from variant.models import Reference, ReferenceGenome


class Command(BaseCommand):
    """Insert Reference genome sequence and annotation IDs"""

    help = 'Insert Reference genome sequence and annotation IDs'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--reference', metavar='REFERENCE',
                            default='gi|29165615|ref|NC_002745.2|',
                            help=('Reference genome.'))
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        # Get Reference sequence
        try:
            reference = Reference.objects.get(name=opts['reference'])
        except Reference.DoesNotExist:
            raise CommandError('Missing Reference: {0} == Exiting.'.format(
                opts['reference']
            ))

        sql = """SELECT reference_position, reference_base, annotation_id
                 FROM variant_snp
                 WHERE reference_id={0}
                 ORDER BY reference_position;""".format(reference.pk)
        reference_genome = OrderedDict()
        for row in query_database(sql):
            if row['reference_position'] not in reference_genome:
                reference_genome[row['reference_position']] = {
                    'base': row['reference_base'],
                    'annotation_id': row['annotation_id']
                }

        if len(reference_genome) != reference.length:
            raise CommandError(
                f'Length Mismatch {len(reference_genome)} {reference.length}')

        if opts['empty']:
            print("Emptying Variant ReferenceGenome Table")
            ReferenceGenome.objects.filter(reference=reference).delete()
        try:
            print("Inserting Variant ReferenceGenome Table")
            ReferenceGenome.objects.create(
                reference=reference,
                sequence=reference_genome
            )
        except IntegrityError as e:
            raise CommandError(f'{e}')
