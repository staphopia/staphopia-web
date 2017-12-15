"""Insert the sumamry statistics for sample sequence."""

import json
from django.core.management.base import BaseCommand, CommandError

from sample.tools import get_analysis_status, get_sample
from version.tools import get_pipeline_version
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
        files, missing = get_analysis_status(opts['name'], opts['sample_dir'])

        sample = get_sample(opts['user'], opts['name'],
                            files['fastq_original_md5'])
        version = get_pipeline_version(files['version'])

        # Insert analysis results
        insert_sequence_stats(files, sample, version, force=opts['force'])
