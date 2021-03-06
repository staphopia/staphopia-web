""" Insert Jellyfish output into the database. """
import sys
import time

from django.core.management.base import BaseCommand

from kmer.partitions import PARTITIONS


class Command(BaseCommand):
    help = 'Insert Kmer data generated by Jellyfish into the database.'

    _tables = ['kmer_string']

    def add_arguments(self, parser):
        parser.add_argument('counts', metavar='UNIQ_COUNTS',
                            help='Text file of unique kmers (uniq- c).')
        parser.add_argument('outdir', metavar='UNIQ_COUNTS',
                            help='Directory to output fiels to...')

    def handle(self, *args, **opts):
        fh = {}
        for child, parent in PARTITIONS.items():
            fh[parent] = open(
                '{0}/{1}.txt'.format(opts['outdir'], parent), 'w'
            )
        total = 0
        singletons = 0
        with open(opts['counts'], "r") as f:
            for line in f:
                line = line.strip()
                count, kmer = line.split(' ')

                # Lets skip singletons for now!
                if int(count) > 1:
                    child = kmer[-7:]
                    parent = PARTITIONS[child]
                    fh[parent].write('{0}\n'.format(kmer))
                    total += 1
                    # Process every 100k kmers
                    if total % 100000 == 0:
                        print(("Written {0} kmers, "
                               "skipped {1} singletons...").format(
                            total, singletons
                        ))
                elif int(count) == 1:
                    singletons += 1

        print(("Written {0} kmers, skipped {1} singletons...").format(
            total, singletons
        ))
