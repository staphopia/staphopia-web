"""Verify an analysis completed."""
import glob
import os
from django.core.management.base import BaseCommand
from sample.tools import get_analysis_status, print_analysis_status


class Command(BaseCommand):
    """Verify an analysis completed."""

    help = 'Verify an analysis completed.'

    def add_arguments(self, parser):
        parser.add_argument('directory', metavar='DIRECTORY',
                            help=('Directory of samples to verify.'))
        parser.add_argument('--incomplete', action='store_true',
                            help='Only print incomplete samples.')
        parser.add_argument('--split', action='store_true',
                            help='Split sample tags.')
        parser.add_argument('--single', action='store_true',
                            help='Input is only a single sample.')
        parser.add_argument('--optional', action='store_true',
                            help='Do not require all files to exist.')
        parser.add_argument('--sample_tag',  type=str, default=None,
                            help='Sample tag used in analysis.')

    def handle(self, *args, **opts):
        """Verify an analysis completed."""
        samples = None
        if opts['single']:
            samples = [opts['directory']]
        else:
            samples = glob.glob('{0}/*'.format(opts['directory']))

        for sample_dir in samples:
            if os.path.isdir(sample_dir):
                sample = os.path.basename(sample_dir.rstrip('/'))
                found, missing = get_analysis_status(sample, sample_dir,
                                                     optional=opts['optional'])
                print_analysis_status(sample, found, missing,
                                      print_incomplete=opts['incomplete'])
