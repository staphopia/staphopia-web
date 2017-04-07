"""Verify an analysis completed."""

from os.path import basename
import glob

from django.core.management.base import BaseCommand

from sample.tools import validate_analysis


class Command(BaseCommand):
    """Verify an analysis completed."""

    help = 'Verify an analysis completed.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('dir', metavar='DIRECTORY',
                            help=('Directory of samples to verify.'))
        parser.add_argument('--incomplete', action='store_true',
                            help='Only print incomplete samples.')
        parser.add_argument('--split', action='store_true',
                            help='Split sample tags.')

    def handle(self, *args, **opts):
        """Verify an analysis completed."""
        # Validate all files are present
        for sample_dir in glob.glob('{0}/*'.format(opts['dir'])):
            sample_tag = basename(sample_dir)

            if opts['split']:
                sample_tag = sample_tag.split('_')[1]

            files = validate_analysis(sample_dir, sample_tag, optional=True,
                                      print_incomplete=opts['incomplete'])

            if not opts['incomplete']:
                if files:
                    print('{0}\tOK'.format(sample_tag))
                else:
                    print('{0}\tINCOMPLETE'.format(sample_tag))

