""" Output unique kmers to file. """
import os
import psutil
import sys
from subprocess import check_output, CalledProcessError, STDOUT

from django.core.management.base import BaseCommand

from staphopia.utils import timeit, gziplines


def current_memory():
    process = psutil.Process(os.getpid())
    return int(process.memory_info()[0] / float(2 ** 20))


def valid_gzfile(gzfile):
    try:
        check_output(['gunzip', '-t', gzfile], stderr=STDOUT)
        return True
    except CalledProcessError:
        return False


class Command(BaseCommand):
    help = 'Output unique kmers to file.'

    def add_arguments(self, parser):
        parser.add_argument('jellyfish', metavar='JELLYFISH_COUNTS',
                            help=('List of compressed (gzip) Jellyfish '
                                  'files to pull unique kmers from.'))
        parser.add_argument('output', metavar='OUTPUT_PREFIX',
                            help='Prefix to output unique kmers to.')

    def handle(self, *args, **opts):
        # Read Jellyfish file
        self.kmers = {}
        self.total = 1
        self.count = 1
        self.prefix = opts['output']
        with open(opts['jellyfish'], 'r') as fh:
            for line in fh:
                line = line.rstrip()
                if valid_gzfile(line):
                    self.read_jellyfish_counts(line.rstrip())

                    if current_memory() > 50000:
                        self.dump_kmers()
                else:
                    self.dump_bad_file(line)

        self.dump_kmers()
        sys.exit()

    @timeit
    def read_jellyfish_counts(self, jellyfish_file):
        for line in gziplines(jellyfish_file):
            kmer, count = line.rstrip().split(' ')
            self.kmers[kmer] = True
        print '{0}:{1}:{2}:{3}'.format(
            self.total, current_memory(), len(self.kmers), jellyfish_file
        )
        self.total += 1

    @timeit
    def dump_kmers(self):
        output = "{0}_{1:04d}.txt".format(self.prefix, self.count)
        self.count += 1
        print '{0}:Dumping kmers to {1}...'.format(current_memory(), output)
        with open(output, 'w') as fh_out:
            for kmer in self.kmers:
                fh_out.write("{0}\n".format(kmer))

        # Clear kmer dict to free up memory
        self.kmers.clear()

    @timeit
    def dump_bad_file(self, bad_file):
        output = "{0}_corrupted.txt".format(self.prefix)
        print '{0}:Invalid gzip format, skipping...'.format(bad_file)
        with open(output, 'a') as fh_out:
            fh_out.write("{0}\n".format(bad_file))
