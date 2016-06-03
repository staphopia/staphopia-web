"""Insert the metadata fields into the database."""

from django.db import transaction
from django.core.management.base import BaseCommand

from sample.models import MetaData


class Command(BaseCommand):
    """Insert the metadata fields into the database."""

    help = 'Insert the metadata fields into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('metadata', metavar='METADATA',
                            help=('Tab delimited (field, description) of '
                                  'metadata fields to be added.'))

    @transaction.atomic
    def handle(self, *args, **opts):
        """Get or Create MetaData fields."""
        # Validate all files are present
        with open(opts['metadata'], 'r') as fh:
            for line in fh:
                field, description = line.rstrip().split('\t')
                metadata_obj, created = MetaData.objects.get_or_create(
                    field=field, description=description
                )
                print("{0}\t{1}".format(field, created))
