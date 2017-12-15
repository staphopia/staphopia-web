"""Insert MLST results into database."""
from django.core.management.base import BaseCommand

from mlst.tools import (
    insert_mlst,
    insert_report,
    parse_ariba,
    parse_blast,
    parse_mentalist
)
from sample.tools import get_analysis_status, get_sample
from version.tools import get_pipeline_version


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
        files, missing = get_analysis_status(opts['name'], opts['sample_dir'])

        sample = get_sample(opts['user'], opts['name'],
                            files['fastq_original_md5'])
        version = get_pipeline_version(files['version'])

        st = {'ariba': 0}
        report = {'ariba': 'empty'}
        if 'fastq_r2' in files:
            # Ariba only works on paired end reads
            st['ariba'], report['ariba'] = parse_ariba(
                files['mlst_ariba_mlst_report'],
                files['mlst_ariba_details']
            )

        st['mentalist'], report['mentalist'] = parse_mentalist(
            files['mlst_mentalist'],
            files['mlst_mentalist_ties'],
            files['mlst_mentalist_votes']
        )

        st['blast'], report['blast'] = parse_blast(files['mlst_blastn'])

        insert_mlst(sample, version, st, force=opts['force'])
        insert_report(sample, version, report, force=opts['force'])
