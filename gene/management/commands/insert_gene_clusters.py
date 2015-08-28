""" Insert UniRef90 gene clusters into the database. """
from django.core.management.base import BaseCommand

from staphopia.utils import read_fasta
from gene.models import Clusters


class Command(BaseCommand):
    help = 'Insert UniRef90 gene clusters into the database.'

    def add_arguments(self, parser):
        parser.add_argument('list', metavar='UNIREF90_LIST',
                            help=('A list of UniRef90 Cluster IDs to insert '
                                  'into the database.'))
        parser.add_argument('proteins', metavar='UNIREF90_FASTA',
                            help=('A FASTA file containing protein sequences '
                                  'to extract clusters from.'))

    def handle(self, *args, **opts):
        # Read Fasta files
        self.proteins = read_fasta(opts['proteins'], compressed=True)

        # Read cluster IDs and append
        clusters = []
        with open(opts['list'], 'r') as fh:
            for line in fh:
                line = line.rstrip()
                clusters.append(Clusters(name=line, aa=self.proteins[line]))

        # Insert clusters to database
        Clusters.objects.bulk_create(clusters, batch_size=1000)
