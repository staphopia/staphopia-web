"""Empty results for each sample from database."""
import sys

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

TABLES_TO_EMPTY = [
    'variant_toindel',
    'variant_tosnp',
    'variant_counts',
    'variant_snpcounts',
    'assembly_contigs',
    'assembly_stats',
    'gene_blastresults',
    'gene_features',
    'mlst_blast',
    'mlst_srst2',
    'sccmec_coverage',
    'sccmec_primers',
    'sccmec_proteins',
    'sequence_stat',
    'sample_sample',
]

class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')
        parser.add_argument('--for_real_empty', action='store_true',
                            help='Empty tables and reset counts.')

    def handle(self, *args, **opts):
        """Insert results to database."""
        if opts['empty'] and opts['for_real_empty']:
            # Empty Tables
            self.empty_tables()
            sys.exit()

    @transaction.atomic
    def empty_tables(self):
        """Empty Tables and Reset id counters to 1."""
        for table in TABLES_TO_EMPTY:
            self.empty_table(table)

    def empty_table(self, table):
        """Empty Table and Reset id counters to 1."""
        print("Emptying {0}...".format(table))
        query = "TRUNCATE TABLE {0} RESTART IDENTITY CASCADE;".format(table)
        cursor = connection.cursor()
        cursor.execute(query)
