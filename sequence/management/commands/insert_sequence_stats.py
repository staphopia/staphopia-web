"""Insert the sumamry statistics for sample sequence."""
from django.core.management.base import BaseCommand

from sample.tools import prep_insert
from sequence.tools import insert_sequence_stats


class Command(BaseCommand):
    """Insert the sumamry statistics for sample sequence."""

    help = 'Insert the summary statistics for sample sequence.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('user', metavar='USERNAME',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('sample_dir', metavar='SAMPLE_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('name', metavar='SAMPLE_NAME',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')

    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all files are present, will cause error if files are missing
        sample, version, files = prep_insert(
            opts['user'], opts['name'], opts['sample_dir']
        )
        insert_sequence_stats(sample, version, files, force=opts['force'])
