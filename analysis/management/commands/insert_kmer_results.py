'''
    Robert Petit
    
    Insert Jellyfish output into the database
'''
import sys
import gzip
import os.path
from optparse import make_option

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import PipelineVersions, Kmer, KmerString, KmerCount, KmerTotal

class Command(BaseCommand):
    help = 'Insert Kmer data into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--jellyfish', dest='jellyfish',
                    help='Gzipped jellyfish output.'),
        make_option('--sample_id', dest='sample_id',
                    help='Sample id of the data.'),
        make_option('--empty', dest='empty', action='store_true',
                    help='Empty each of the tables'),
        make_option('--pipeline_version', dest='pipeline_version',
                    help='Version of the pipeline used in this analysis.'),
        make_option('--debug', action='store_true', dest='debug', 
                    default=False, help='Will not write to the database'),
        )
     
    def handle(self, *args, **options):
        # Required Parameters
        if not options['empty']:
            if not options['jellyfish']:
                raise CommandError('--jellyfish is requried')
            elif not options['sample_id']:
                raise CommandError('--sample_id is requried')
            elif not options['pipeline_version']:
                raise CommandError('--pipeline_version is requried')
        else:
            # Dangerous just exit for now
            #self.empty_tables()
            sys.exit()
            
        # Test input files
        if not os.path.exists(options['jellyfish']):
            raise CommandError('{0} is missing'.format(options['jellyfish']))
            
        # Make sure sample_id exists
        try:
            sample = Sample.objects.get(pk=options['sample_id'])
        except Sample.DoesNotExist:
            raise CommandError('sample_id {0} does not exist'.format(
                options['sample_id']
            ))
            
        # Pipeline Version
        try:
            pipeline_version = PipelineVersions.objects.get_or_create(
                module='kmer', 
                version=options['pipeline_version']
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
        fh = gzip.open(options['jellyfish'])
        
        for line in fh:
            word, count = line.rstrip().split(' ')
            kmers[word] = int(count)
            if word not in kmer_string:
                self.kmer_strings.append(KmerString(string=word))
            if len(kmers) % 100000 == 0:
                print '{0} kmers processed'.format(len(kmers))
            total += kmers[word]
        fh.close()
        
        # Insert all the new strings, get updated KmerString
        if len(self.kmer_strings) > 0:
            kmer_string = self.insert_kmer_strings()
            
        kmer_string_instances = self.get_kmer_string_instances()
        print 'Processing Counts'
        for word,count in kmers.iteritems():
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
        KmerString.objects.bulk_create(self.kmer_strings, 
                                       batch_size=100000)
        return self.get_kmer_strings()
        
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
        KmerCount.objects.bulk_create(self.kmer_counts, batch_size=100000)
        
    @transaction.atomic
    def insert_kmer_total(self, kmer, total):
        kmer_total = KmerTotal.objects.get_or_create(kmer=kmer, total=total)
        
    def empty_tables(self):
        KmerCount.objects.all().delete()
        KmerString.objects.all().delete()
        KmerTotal.objects.all().delete()
        Kmer.objects.all().delete()