"""Insert the results of sample analysis into the database."""

import json
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import md5sum
from sample.models import Sample
from sample.tools import validate_analysis
from sccmec.tools import insert_sccmec_coverage, insert_sccmec_blast


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_dir', metavar='SAMPLE_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')

    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all files are present
        print("Validating required files are present...")
        files = validate_analysis(opts['sample_dir'], opts['sample_tag'])
        fq_md5sum = md5sum('{0}/{1}.cleanup.fastq.gz'.format(
            opts['sample_dir'], opts['sample_tag']
        ))

        # Test if results already inserted
        sample = None
        try:
            sample = Sample.objects.get(md5sum=fq_md5sum)
            print("Found existing sample: {0} ({1})".format(
                sample.sample_tag, sample.md5sum
            ))
        except Sample.DoesNotExist:
            # Create new sample
            raise CommandError('Sample should already exist.')

        # Insert analysis results
        '''
        print("Inserting SCCmec Coverage Stats...")
        insert_sccmec_coverage(files['sccmec_coverage'], sample,
                               force=opts['force'])
        insert_sccmec_blast(files['sccmec_primers'], sample, is_primers=True,
                            force=opts['force'])
        insert_sccmec_blast(files['sccmec_proteins'], sample, is_primers=False,
                            force=opts['force'])
        '''
        print("Inserting SCCmec subtype BLAST results...")
        insert_sccmec_blast(files['sccmec_subtypes'], sample, is_primers=False,
                            is_subtype=True)
        print("Insert Complete")
