"""Insert the results of sample analysis into the database."""

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import md5sum
from sample.models import Sample

from sample.tools import validate_analysis
from kmer.tools import format_kmer_counts


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('sample_dir', metavar='SAMPLE_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('outdir', metavar='OUTPUT_DIRECTORY',
                            help=('Sample tag associated with sample.'))

    @transaction.atomic
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
                sample.db_tag, sample.md5sum
            ))
        except Sample.DoesNotExist:
            # Create new sample
            raise CommandError('Sample should already exist.')

        # Formating kmer results
        format_kmer_counts(files['kmers'], sample, opts['outdir'])
