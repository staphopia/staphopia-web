""" Insert Jellyfish output into the database. """
import sys
import gzip
import os.path
from optparse import make_option

from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import PipelineVersions
from analysis.models import Kmer, KmerString, KmerCount, KmerTotal


class Command(BaseCommand):
    help = 'Insert Kmer data into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--jellyfish', dest='jellyfish',
                    help='Gzipped jellyfish output.'),
        make_option('--sample_tag', dest='sample_tag',
                    help='Sample tag of the data.'),
        make_option('--empty', dest='empty', action='store_true',
                    help='Empty each of the tables'),
        make_option('--pipeline_version', dest='pipeline_version',
                    help=('Version of the pipeline used in this analysis. '
                          '(Default: 0.1)')),
        make_option('--debug', action='store_true', dest='debug',
                    default=False, help='Will not write to the database'),
    )

    def handle(self, *args, **opts):
        # Required Parameters
        if not opts['empty']:
            if not opts['jellyfish']:
                raise CommandError('--jellyfish is requried')
            elif not opts['sample_tag']:
                raise CommandError('--sample_tag is requried')
            elif not opts['pipeline_version']:
                opts['pipeline_version'] = "0.1"
        else:
            # Dangerous just exit for now
            # self.empty_tables()
            sys.exit()

        # Test input files
        if not os.path.exists(opts['jellyfish']):
            raise CommandError('{0} is missing'.format(opts['jellyfish']))

        # Make sure sample_id exists
        try:
            sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('sample_tag {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Pipeline Version
        try:
            pipeline_version = PipelineVersions.objects.get_or_create(
                module='kmer',
                version=opts['pipeline_version']
            )[0]
        except PipelineVersions.DoesNotExist:
            raise CommandError('Error saving pipeline information')

        # Get KmerString
        kmer_string = self.get_kmer_strings()

        # Read through jellyfish kmer counts
        kmer, created = Kmer.objects.get_or_create(sample=sample,
                                                   version=pipeline_version)
        kmers = {}
        self.kmer_strings = []
        self.kmer_counts = []
        total = 0
        fh = gzip.open(opts['jellyfish'])

        for line in fh:
            word, count = line.rstrip().split(' ')
            kmers[word] = int(count)
            if word not in kmer_string:
                self.kmer_strings.append(word)
                if len(self.kmer_strings) == 1000:
                    self.insert_kmer_strings()
                    self.kmer_strings = []
            if len(kmers) % 100000 == 0:
                # Insert all the new strings, get updated KmerString
                if len(self.kmer_strings) > 0:
                    self.insert_kmer_strings()
                    self.kmer_strings = []
                print '{0} kmers processed'.format(len(kmers))
            total += kmers[word]
        fh.close()

        # Insert remaining kmer_strings
        if len(kmers) % 100000 > 0:
            self.insert_kmer_strings()

        kmer_string_instances = self.get_kmer_string_instances()
        print 'Processing Counts'
        for word, count in kmers.iteritems():
            id = kmer_string[word]
            self.kmer_counts.append(KmerCount(kmer=kmer,
                                              string=kmer_string_instances[id],
                                              count=count))

        print 'Inserting Counts'
        self.insert_kmer_counts()

        print 'Inserting Total'
        self.insert_kmer_total(kmer, total)

    def insert_kmer_strings(self):
        print 'Inserting new kmers'
        cur = connection.cursor()
        vals = ','.join(["('{0}')".format(x) for x in self.kmer_strings])
        cur.execute("INSERT INTO analysis_kmerstring (string) VALUES " + vals)
        return True

    def get_kmer_strings(self):
        kmer_strings = {}
        for ks in KmerString.objects.all():
            kmer_strings[ks.string] = ks.pk
        return kmer_strings

    def get_kmer_string_instances(self):
        pks = []
        for ks in KmerString.objects.all():
            pks.append(ks.pk)
        return KmerString.objects.in_bulk(pks)

    @transaction.atomic
    def insert_kmer_counts(self):
        KmerCount.objects.bulk_create(self.kmer_counts, batch_size=1000)

    @transaction.atomic
    def insert_kmer_total(self, kmer, total):
        kmer_total = KmerTotal.objects.get_or_create(kmer=kmer, total=total)
        return kmer_total

    def empty_tables(self):
        KmerCount.objects.all().delete()
        KmerString.objects.all().delete()
        KmerTotal.objects.all().delete()
        Kmer.objects.all().delete()
