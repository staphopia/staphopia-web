"""Insert variant analysis results into database."""
import sys

from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import read_fasta
from variant.models import Reference, ReferenceGenome


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('input', metavar='INPUT_FASTA',
                            help=('FASTA formated file to be inserted'))
        parser.add_argument('--compressed', action='store_true',
                            help='Input FASTA is gzipped.')
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')

    def handle(self, *args, **opts):
        """Insert results to database."""
        if opts['empty']:
            # Empty Tables
            self.empty_tables()
            sys.exit()

        fasta = read_fasta(opts['input'], compressed=opts['compressed'])
        for ref, sequence in fasta.items():
            try:
                reference = Reference.objects.get(name=ref)
            except Reference.DoesNotExist:
                raise CommandError('Missing Reference: {0} == Exiting.'.format(
                    ref
                ))

            reference.sequence = sequence
            reference.save()

    @transaction.atomic
    def empty_tables(self):
        """Empty Tables and Reset id counters to 1."""
        tables = ['variant_referencegenome']

        for table in tables:
            self.empty_table(table)

    def empty_table(self, table):
        """Empty Table and Reset id counters to 1."""
        print("Emptying {0}...".format(table))
        query = "TRUNCATE TABLE {0} RESTART IDENTITY CASCADE;".format(table)
        cursor = connection.cursor()
        cursor.execute(query)
