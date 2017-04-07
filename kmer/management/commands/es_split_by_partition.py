"""Insert the results of sample analysis into the database."""
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from staphopia.utils import md5sum
from sample.models import Sample

from kmer.partitions import PARTITIONS
from kmer.tools import (
    get_samples, format_sample_pk, jellyfish_dump, insert_kmer_stats
)


class Command(BaseCommand):
    """Insert the results of sample analysis into the database."""

    help = 'Insert the results of sample analysis into the database.'

    def add_arguments(self, parser):
        """Command line arguements."""
        parser.add_argument('project_dir', metavar='PROJECT_DIRECTORY',
                            help=('User name for the owner of the sample.'))
        parser.add_argument('outdir', metavar='OUTPUT_DIRECTORY',
                            help=('Sample tag associated with sample.'))
        parser.add_argument('--append', action='store_true',
                            help='Append to existing files.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """Insert the results of sample analysis into the database."""
        # Validate all samples are in the database, before we do anything
        self.kmers = {}
        self.total_kmers = 0
        self.append = opts['append']
        samples = get_samples(opts['project_dir'])
        total_samples = len(samples.keys())
        print('Found {0} samples, validating database existence...'.format(
            total_samples
        ))
        for k, v in samples.items():
            fq_md5sum = None
            with open(v['fq'], 'r') as fh:
                fq_md5sum = fh.readline().split()[0]
            # Test if results already inserted
            sample = None
            try:
                sample = Sample.objects.get(md5sum=fq_md5sum)
                samples[k]['sample_id'] = format_sample_pk(sample.pk)
                samples[k]['sample_obj'] = sample
                samples[k]['process'] = True
            except Sample.DoesNotExist:
                print('Skip {0}, does not exist in the database.'.format(k))
            break

        # All samples are in the database, we can do work now
        n = 0
        print('All samples accounted for. Processing Jellyfish counts...')
        self.open_file_handles(opts['outdir'])
        for k, v in samples.items():
            if v['process']:
                total, singletons = self.process_jellyfish(v['jf'],
                                                           v['sample_id'])
                insert_kmer_stats(v['sample_obj'], total, singletons)
                n += 1
                print('{0} of {1} samples processed.'.format(n, total_samples))
        self.close_file_handles()

    def open_file_handles(self, outdir):
        """Open filehandles."""
        self.fh = {}
        for child, parent in PARTITIONS.items():
            output = '{0}/{1}.txt'.format(outdir, parent)
            if self.append:
                self.fh[parent] = open(output, 'a')
            else:
                self.fh[parent] = open(output, 'w')

    def close_file_handles(self):
        """Close all open file handles."""
        for child, parent in PARTITIONS.items():
            self.fh[parent].close()

    def process_jellyfish(self, jf_file, sample_id):
        """Loop through kmers."""
        total = 0
        singletons = 0
        for line in jellyfish_dump(jf_file):
            if not line:
                continue
            kmer, count = line.rstrip().split()
            sample_name = '{0}-{1}'.format(sample_id, count)

            # Write kmers
            child = kmer[-7:]
            parent = PARTITIONS[child]
            self.fh[parent].write('{0}\t{1}\n'.format(kmer, sample_name))

            total += 1
            if int(count) == 1:
                singletons += 1

        return [total, singletons]
