"""
update_centernames.

Update database with corrected Center Names.
"""
import sys

from django.db import transaction
from django.core.management.base import BaseCommand

from ena.models import CenterNames


class Command(BaseCommand):
    """Update database with corrected Center Names."""

    help = 'Update database with corrected Center Names.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('names',
                            help=('Tab-delimted text file containing '
                                  'corrected sequencing center names.'))
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')

    @transaction.atomic
    def handle(self, *args, **options):
        """Query ENA and retrieve latest results."""
        if options['empty']:
            print("Deleting existing Center Names...")
            CenterNames.objects.all().delete()
            sys.exit()
        else:
            with open(options['names'], 'r') as fh:
                for line in fh:
                    if line.startswith('ENA'):
                        pass
                    else:
                        ena_name, center_name, link = line.rstrip().split('\t')
                        center, created = CenterNames.objects.get_or_create(
                            ena_name=ena_name,
                            name=center_name,
                            link=link
                        )
                        print("{0}\t{1}".format(ena_name, created))
