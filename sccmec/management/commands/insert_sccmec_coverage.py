"""Insert SCCmec cassette coverage into database."""
from django.db import transaction
from django.core.management.base import BaseCommand

from sample.tools import get_sample
from sccmec.tools import insert_sccmec_coverage


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert SCCmec cassette coverage into database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('coverage', metavar='COVERAGE',
                            help='Gzipped GenomeBedCoverage output file.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        sample = get_sample(opts['sample_tag'])
        insert_sccmec_coverage(opts['coverage'], sample)
