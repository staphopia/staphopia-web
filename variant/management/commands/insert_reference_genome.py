"""Insert variant analysis results into database."""
import sys

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import read_fasta
from variant.models import Reference, ReferenceGenome


class Command(BaseCommand):
    """Insert results into database."""

    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('input', metavar='INPUT_FASTA',
                            help=('FASTA formated file to be inserted'))
        parser.add_argument('--compressed', action='store_true',
                            help='Input FASTA is gzipped.')
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert results to database."""
        fasta = read_fasta(opts['input'], compressed=opts['compressed'])
        for ref, sequence in fasta.items():
            if opts['empty']:
                print("Emptying Variant Reference Table")
                Reference.objects.filter(name=ref).delete()
            try:
                Reference.objects.create(
                    name=ref,
                    length=len(sequence),
                    sequence=sequence
                )
            except IntegrityError as e:
                raise CommandError(f'{e}')
