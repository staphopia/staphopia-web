""" Insert MLST results into database. """
import os.path
from optparse import make_option

from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from samples.models import Sample
from analysis.models import (
    MLST,
    MLSTBlast,
    MLSTSrst2,
    PipelineVersion
)


class Command(BaseCommand):

    """ Insert results into database. """

    help = 'Insert the analysis results into the database.'

    option_list = BaseCommand.option_list + (
        make_option('--sample_tag', dest='sample_tag',
                    help='Sample tag for which the data is for'),
        make_option('--blast', dest='blast',
                    help='BLASTN output of MLST results'),
        make_option('--srst', dest='srst',
                    help='SRST output of MLST results'),
        make_option('--pipeline_version', dest='pipeline_version',
                    help=('Version of the pipeline used in this analysis. '
                          '(Default: 0.1)')),
    )

    def handle(self, *args, **opts):
        """ Insert results to database. """
        # Required Parameters
        if not opts['sample_tag']:
            raise CommandError('--sample_tag is requried')
        elif not opts['blast']:
            raise CommandError('--blast is requried')
        elif not opts['srst']:
            raise CommandError('--srst is requried')
        elif not opts['pipeline_version']:
            opts['pipeline_version'] = "0.1"

        # Input File
        if not os.path.exists(opts['blast']):
            raise CommandError('{0} does not exist'.format(opts['blast']))
        elif not os.path.exists(opts['srst']):
            raise CommandError('{0} does not exist'.format(opts['srst']))

        # Sample
        try:
            sample = Sample.objects.get(sample_tag=opts['sample_tag'])
        except Sample.DoesNotExist:
            raise CommandError('sample_tag: {0} does not exist'.format(
                opts['sample_tag']
            ))

        # Pipeline Version
        try:
            pipeline_version, created = PipelineVersion.objects.get_or_create(
                module='mlst',
                version=opts['pipeline_version']
            )
        except PipelineVersion.DoesNotExist:
            raise CommandError('Error saving pipeline information')

        # MLST
        try:
            mlst, created = MLST.objects.get_or_create(
                sample=sample,
                version=pipeline_version
            )
        except IntegrityError as e:
            raise CommandError('MLST Error: {0}'.format(e))

        # Insert Blast Results
        blast_results = open(opts['blast'], 'r')
        for line in blast_results:
            line = line.rstrip()
            # 0sseqid 1bitscore 2slen 3length 4gaps 5mismatch 6pident 7evalue
            cols = line.split('\t')
            locus_name, locus_id = cols[0].split('-')
            locus_name = locus_name.replace('_', '')

            try:
                MLSTBlast.objects.create(
                    mlst=mlst,
                    locus_name=locus_name,
                    locus_id=locus_id,
                    bitscore=cols[1],
                    slen=cols[2],
                    length=cols[3],
                    gaps=cols[4],
                    mismatch=cols[5],
                    pident=cols[6],
                    evalue=cols[7]
                )
                print "BLASTN Results Saved"
            except IntegrityError as e:
                raise CommandError('MLSTBlast Error: {0}'.format(e))
        blast_results.close()

        # Insert SRST2 Results
        srst_results = open(opts['srst'], 'r')
        srst_results.readline()
        results = srst_results.readline().rstrip().split('\t')
        srst_results.close()

        try:
            # 0:Sample  1:ST    2:arcc  3:aroe  4:glpf  5:gmk_  6:pta_  7:tpi_
            # 8:yqil    9:mismatches    10:uncertainty  11:depth    12:maxMAF
            MLSTSrst2.objects.create(
                mlst=mlst,
                ST=results[1],
                arcc=results[2],
                aroe=results[3],
                glpf=results[4],
                gmk=results[5],
                pta=results[6],
                tpi=results[7],
                yqil=results[8],
                mismatches=results[9],
                uncertainty=results[10],
                depth=float(results[11]),
                maxMAF=float("{0:.7f}".format(float(results[12])))
            )
            print "SRST2 Results Saved"
        except IntegrityError as e:
            raise CommandError('MLSTSrst2 Error: {0}'.format(e))
