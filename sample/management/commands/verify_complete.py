"""Verify an analysis completed."""
import os
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
        parser.add_argument('--single', action='store_true',
                            help='Input is only a single sample.')
        parser.add_argument('--sample_tag',  type=str, default=None,
                            help='Sample tag used in analysis.')

    def handle(self, *args, **opts):
        """Verify an analysis completed."""
        # Validate all files are present
        samples = None
        if opts['single']:
            samples = [opts['dir']]
        else:
            samples = glob.glob('{0}/*'.format(opts['dir']))

        for sample_dir in samples:
            sample_tag = basename(sample_dir.rstrip('/'))
            if opts['sample_tag']:
                sample_tag = opts['sample_tag']

            if opts['split']:
                sample_tag = sample_tag.split('_')[1]

            files = validate_analysis(sample_dir, sample_tag, optional=True,
                                      print_incomplete=opts['incomplete'])

            if not opts['incomplete']:
                if files:
                    print('{0}\tOK'.format(sample_tag))
                else:
                    print('{0}\tINCOMPLETE'.format(sample_tag))
