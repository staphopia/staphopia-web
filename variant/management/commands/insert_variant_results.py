"""Insert the results of sample analysis into the database."""

import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from sample.models import Sample

from variant.tools import insert_variant_results


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('vcf', metavar='VARIANTS_VCF',
                            help=('Variants in VCF format.'))
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--force', action='store_true',
                            help='Force updates for existing entries.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""

        # Test if results already inserted
        sample = None
        try:
            sample = Sample.objects.get(
                sample_tag=opts['sample_tag']
            )
            print("Found existing sample: {0} ({1})".format(
                sample.sample_tag, sample.md5sum
            ))
            if not opts['force']:
                raise CommandError(
                    'Sample exists, please use --force to use it.'
                )
        except Sample.DoesNotExist:
            raise CommandError(
                    'Sample does not exist, please load the sample.'
                )

        # Insert analysis results
        print("Inserting Variants...")
        insert_variant_results(opts['vcf'], sample, force=opts['force'])
