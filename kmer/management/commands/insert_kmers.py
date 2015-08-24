""" Insert Jellyfish output into the database. """
import gzip
import sys
import time

from bitarray import bitarray

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import PipelineVersion
from kmer.models import Kmer, KmerBinary, KmerTotal


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r\t%2.2f sec' % (method.__name__, te - ts)
        return result

    return timed


class Command(BaseCommand):
    help = 'Insert Kmer data generated by Jellyfish into the database.'

    _code = {
        'A': bitarray('01'),
        'C': bitarray('11'),
        'G': bitarray('00'),
        'T': bitarray('10')
    }

    _tables = [
        'kmer_kmerbinarytmp',
        'kmer_kmercount',
        'kmer_kmertotal',
        'kmer_kmer',
    ]

    def add_arguments(self, parser):
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('jellyfish', metavar='JELLYFISH_COUNTS',
                            help=('Compressed (gzip) Jellyfish counts to be '
                                  'inserted.'))
        parser.add_argument('--pipeline_version', type=str, default="0.1",
                            help=('Version of the pipeline used in this '
                                  'analysis. (Default: 0.1)'))
        parser.add_argument('--empty', action='store_true',
                            help='Empty tables and reset counts.')

    def handle(self, *args, **opts):
        if opts['empty']:
            # Empty Tables
            self.empty_tables()
            sys.exit()

        # Get Sample instance
        try:
            sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('sample_tag {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Get PipelineVersion instance
        try:
            pipeline_version = PipelineVersion.objects.get_or_create(
                module='kmer',
                version=opts['pipeline_version']
            )[0]
        except PipelineVersion.DoesNotExist:
            raise CommandError('Error saving pipeline information')

        # Create kmer instance
        try:
            self.kmer_instance = Kmer.objects.create(
                sample=sample,
                version=pipeline_version
            )
        except IntegrityError:
            raise CommandError(
                'Kmer entry already exists for {0} ({1})'.format(
                    sample, pipeline_version
                )
            )

        # Inititalize values
        self.total = 0
        self.singletons = 0
        self.kmer_counts = {}
        self.kmer_binary = []
        self.new_kmers = 0

        # Read Jellyfish file
        self.read_jellyfish_counts(opts['jellyfish'])
        self.encode_words(self.kmer_counts.keys())

        # Split words into 100k chunks
        start_time = time.time()
        self.insert_kmer(self.encoded_words.keys())
        values = self.get_kmer_binary_inbulk(self.encoded_words.keys())
        # for chunk in self.chunks(values, 20):
        self.insert_counts(values)
        print '{0}\t{1:.2f}'.format(
            len(self.encoded_words),
            (time.time() - start_time)
        )

        # Process remaining kmers and insert totals
        runtime = int(time.time() - start_time)
        KmerTotal.objects.create(
            kmer=self.kmer_instance,
            total=self.total,
            singletons=self.singletons,
            new_kmers=self.new_kmers,
            runtime=runtime
        )

    def encode(self, seq):
        a = bitarray()
        a.encode(self._code, seq)
        return a.tobytes()

    def decode(self, seq):
        a = bitarray()
        a.frombytes(seq)
        return a.decode(self._code)[0:31]

    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l. """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    @timeit
    def read_jellyfish_counts(self, jellyfish_file):
        fh = gzip.open(jellyfish_file)
        for line in fh:
            word, count = line.rstrip().split(' ')
            self.kmer_counts[word] = int(count)

            # increment totals
            self.total += 1
            if int(count) == 1:
                self.singletons += 1
        fh.close()

    @timeit
    def encode_words(self, words):
        # Encode kmers
        self.encoded_words = {}
        for word in words:
            self.encoded_words[self.encode(word)] = word

    @timeit
    def insert_kmer(self, words):
        # Insert bit encoded kmers
        self.new_kmers += KmerBinary.objects.bulk_create_new(words)

        return None

    @timeit
    def get_kmer_binary_inbulk(self, words):
        values = []
        query = """
            SELECT b.id, b.string
            FROM kmer_binarytmp AS tmp
            LEFT JOIN kmer_binary AS b
            ON b.string=tmp.string;
            """
        cursor = connection.cursor()
        cursor.execute(query)

        for row in cursor.fetchall():
            # count, kmer_id, string_id
            values.append('({0}, {1}, {2})'.format(
                self.kmer_counts[self.encoded_words[str(row[1])]],
                self.kmer_instance.pk,
                row[0]
            ))

        return values

    @timeit
    @transaction.atomic
    def insert_counts(self, values):
        for chunk in self.chunks(values, 1000000):
            query = (
                "INSERT INTO kmer_kmercount (count, kmer_id, string_id) "
                "VALUES {0}".format(','.join(chunk))
            )
            cursor = connection.cursor()
            cursor.execute(query)

    @transaction.atomic
    def empty_tables(self):
        # Empty Tables and Reset id counters to 1
        for table in self._tables:
            self.empty_table(table)

    def empty_table(self, table):
        query = "TRUNCATE TABLE {0} RESTART IDENTITY CASCADE;".format(table)
        cursor = connection.cursor()
        cursor.execute(query)
