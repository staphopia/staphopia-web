""" Insert SCCmec cassette coverage into database. """
import numpy
import os.path

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand, CommandError

from sample.models import MetaData
from sccmec.models import Cassette, Coverage
from staphopia.utils import gziplines


class Command(BaseCommand):

    """ Insert results into database. """

    help = 'Insert SCCmec cassette coverage into database.'

    def add_arguments(self, parser):
        """ Make some arguements. """
        parser.add_argument('sample_tag', metavar='SAMPLE_TAG',
                            help='Sample tag of the data.')
        parser.add_argument('coverage', metavar='COVERAGE',
                            help='Gzipped GenomeBedCoverage output file.')

    @transaction.atomic
    def handle(self, *args, **opts):
        """ Insert results to database. """
        if not os.path.exists(opts['coverage']):
            raise CommandError('{0} does not exist'.format(opts['coverage']))

        # Sample (sample.MetaData)
        try:
            sample = MetaData.objects.get(sample_tag=opts['sample_tag'])
        except MetaData.DoesNotExist:
            raise CommandError('sample_tag: {0} does not exist'.format(
                opts['sample_tag']
            ))

        sccmec = {}
        for line in gziplines(opts['coverage']):
            line = line.rstrip()
            header, base, coverage = line.split('\t')

            if header not in sccmec:
                sccmec[header] = {
                    'coverage': [],
                    'total': 0
                }

            if int(coverage):
                sccmec[header]['total'] += 1

            sccmec[header]['coverage'].append(int(coverage))

        for mec_type, stats in sccmec.items():
            np_array = numpy.array(stats['coverage'])

            cassette = Cassette.objects.get(header=mec_type)
            total = float(stats['total']) / cassette.length

            # mecA related
            start = cassette.meca_start - 1
            stop = cassette.meca_stop - 1
            meca_total = 0
            meca = sccmec[header]['coverage'][start:stop]
            for pos in meca:
                if int(pos):
                    meca_total += 1

            try:
                meca_total = float(meca_total) / cassette.meca_length
                meca_array = numpy.array(meca)
            except:
                meca_total = 0.00
                meca_array = None

            try:
                coverage, created = Coverage.objects.get_or_create(
                    sample=sample,
                    cassette=cassette,
                    total=float('{0:.2f}'.format(total)),
                    minimum=min(stats['coverage']),
                    median=numpy.median(np_array),
                    mean=float('{0:.2f}'.format(numpy.mean(np_array))),
                    maximum=max(stats['coverage']),
                    # mecA
                    meca_total=float('{0:.2f}'.format(meca_total)),
                    meca_minimum=min(meca) if meca else 0,
                    meca_median=numpy.median(meca_array) if meca else 0,
                    meca_mean=float(
                        '{0:.2f}'.format(numpy.mean(meca_array))
                    ) if meca else 0.0,
                    meca_maximum=max(meca) if meca else 0
                )
            except IntegrityError:
                created = False

            print '{0}\t{1}\t{2}'.format(sample.sample_tag, mec_type, created)
