"""Insert JSON formatted analysis results into database."""
from django.db import transaction
from django.core.management.base import BaseCommand

from sample.tools import get_sample
from sequence.tools import insert_sequence_stats


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('input', metavar='JSON_INPUT',
                            help='JSON formated file to be inserted')
        parser.add_argument('--is_original', action='store_true',
                            help='Input is for raw sequence. (Default: False')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        sample = get_sample(opts['sample_tag'])
        insert_sequence_stats(opts['input'], sample,
                              is_original=opts['is_original'])
