""" Estimate partitions. """
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Predict optimal substring groupings for partitions.'

    def add_arguments(self, parser):
        parser.add_argument('partitions', metavar='PARTITIONS',
                            help='Two columns of partitions.')

    def handle(self, *args, **opts):
        # Read count file
        partitions = {}
        with open(opts['partitions'], "r") as f:
            for line in f:
                line = line.strip()
                partition, member = line.split('\t')

                if partition not in partitions:
                    partitions[partition] = []

                partitions[partition].append("'{0}'".format(member))

        for partition, members in partitions.iteritems():
            print 'CREATE TABLE kmer_string_{0} ('.format(partition)
            print '    CHECK (substring(string, 25, 31) IN ({0})),'.format(
                ','.join(members)
            )
            print('    LIKE "kmer_string" INCLUDING DEFAULTS INCLUDING '
                  'CONSTRAINTS INCLUDING INDEXES')
            print ') INHERITS (kmer_string);'
