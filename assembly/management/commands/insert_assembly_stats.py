"""Insert JSON formatted assembly results into database."""
from django.db import transaction
from django.core.management.base import BaseCommand

from sample.tools import get_sample
from assembly.tools import insert_assembly_stats


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the assembly results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('input', metavar='JSON_INPUT',
                            help='JSON formated file to be inserted')
        parser.add_argument('--scaffolds', action='store_true',
                            help='Input is scaffolds. (Default: contigs')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        sample = get_sample(opts['sample_tag'])
        if insert_assembly_stats(opts['input'], sample,
                                 is_scaffolds=opts['scaffolds']):
            print("Assembly statistics written to database.")
