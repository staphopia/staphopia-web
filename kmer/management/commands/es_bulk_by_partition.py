"""Insert the results of sample analysis into the database."""
import glob
from os.path import basename, splitext

from django.db import transaction
from django.core.management.base import BaseCommand

from kmer.tools import insert_in_bulk


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('kmers', metavar='KMER_DIRECTORY',
                            help='Directory of kmers seperated by partition.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        files = glob.glob("{0}/*.txt".format(opts['kmers']))
        current = 1
        print("Inserting k-mer counts, will be a while...")
        for f in files:
            partition = splitext(basename(f))[0].lower()
            print("\tWorking on {0} ({1} of {2})".format(
                partition, current, len(files)
            ))
            insert_in_bulk(f, partition)
            current += 1
