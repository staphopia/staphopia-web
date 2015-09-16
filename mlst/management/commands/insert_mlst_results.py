""" Insert MLST results into database. """
import os.path

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from sample.models import MetaData
from mlst.models import Blast, Srst2


class Command(BaseCommand):
    """ Insert results into database. """
    help = 'Insert the analysis results into the database.'

    def add_arguments(self, parser):
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('blast', metavar='BLAST_OUTPUT',
                            help='BLASTN output of MLST results.')
        parser.add_argument('srst', metavar='SRST2_OUTPUT',
                            help='SRST output of MLST results.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Insert results to database. """
        # Input File
        if not os.path.exists(opts['blast']):
            raise CommandError('{0} does not exist'.format(opts['blast']))
        elif not os.path.exists(opts['srst']):
            raise CommandError('{0} does not exist'.format(opts['srst']))

        # Sample (sample.MetaData)
        try:
            sample = MetaData.objects.get(sample_tag=opts['sample_tag'])
        except MetaData.DoesNotExist:
            raise CommandError('sample_tag: {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Insert Blast Results
        print "{0}".format(opts['sample_tag'])
        blast_results = open(opts['blast'], 'r')
        for line in blast_results:
            line = line.rstrip()
            # 0sseqid 1bitscore 2slen 3length 4gaps 5mismatch 6pident 7evalue
            if line:
                cols = line.split('\t')
                locus_name, locus_id = cols[0].split('-')
                locus_name = locus_name.replace('_', '')

                try:
                    blastn, created = Blast.objects.get_or_create(
                        sample=sample,
                        locus_name=locus_name,
                        locus_id=locus_id,
                        bitscore=int(float(cols[1])),
                        slen=cols[2],
                        length=cols[3],
                        gaps=cols[4],
                        mismatch=cols[5],
                        pident=cols[6],
                        evalue=cols[7]
                    )
                    print "BLASTN Results Saved"
                except IntegrityError as e:
                    raise CommandError('{0} MLSTBlast Error: {1}'.format(
                                       opts['sample_tag'], e))
        blast_results.close()

        # Insert SRST2 Results
        srst_results = open(opts['srst'], 'r')
        srst_results.readline()
        results = srst_results.readline().rstrip().split('\t')
        srst_results.close()

        if not results[0]:
            results = ['-'] * 13

        if len(results) == 12:
            results.append('-')

        try:
            # 0:Sample  1:st    2:arcc  3:aroe  4:glpf  5:gmk_  6:pta_  7:tpi_
            # 8:yqil    9:mismatches    10:uncertainty  11:depth    12:maxMAF
            Srst2.objects.create(
                sample=sample,
                st=results[1],
                arcc=results[2],
                aroe=results[3],
                glpf=results[4],
                gmk=results[5],
                pta=results[6],
                tpi=results[7],
                yqil=results[8],
                mismatches=results[9],
                uncertainty=results[10],
                depth=float('0' if results[11] == '-' else results[11]),
                maxMAF=float("{0:.7f}".format(
                    float('0' if results[12] == '-' else results[12])
                ))
            )
            print "SRST2 Results Saved"
        except IntegrityError as e:
            raise CommandError('{0} MLSTSrst2 Error: {1}'.format(
                               opts['sample_tag'], e))
