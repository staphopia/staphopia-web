"""Insert MLST results into database."""
from django.db import transaction
from django.core.management.base import BaseCommand

from sample.tools import get_sample
from mlst.tools import insert_mlst_blast, insert_mlst_srst2


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('blast', metavar='BLAST_OUTPUT',
                            help='BLASTN output of MLST results.')
        parser.add_argument('srst', metavar='SRST2_OUTPUT',
                            help='SRST output of MLST results.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        sample = get_sample(opts['sample_tag'])
        insert_mlst_blast(opts['blast'], sample)
        insert_mlst_srst2(opts['srst'], sample)
