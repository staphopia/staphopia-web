"""Insert MLST results into database."""
from django.core.management.base import BaseCommand

from mlst.tools import insert_mlst
from sample.tools import prep_insert


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the MLST results into the database.'

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
        """Insert results to database."""
        # Validate all files are present, will cause error if files are missing
        sample, version, files = prep_insert(
            opts['user'], opts['name'], opts['sample_dir']
        )

        insert_mlst(sample, version, files, force=opts['force'])
