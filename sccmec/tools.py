"""
Useful functions associated with sccmec.

To use:
from sccmec.tools import UTIL1, UTIL2, etc...
"""
import numpy

from django.db import transaction
from django.db.utils import IntegrityError

from sccmec.models import Cassette, Coverage
from staphopia.utils import gziplines


@transaction.atomic
def insert_sccmec_coverage(coverage, sample):
    """Insert per-base coverage for each SCCmec cassette into the database."""
    sccmec = __read_coverage(coverage)
    for mec_type, stats in sccmec.items():
        np_array = numpy.array(stats['coverage'])

        cassette = Cassette.objects.get(header=mec_type)
        total = float(stats['total']) / cassette.length

        # mecA related
        start = cassette.meca_start - 1
        stop = cassette.meca_stop - 1
        meca_total = 0
        meca = sccmec[cassette.header]['coverage'][start:stop]
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

        print('{0}\t{1}\t{2}'.format(sample.sample_tag, mec_type, created))


def __read_coverage(coverage):
    """Return the per-base coverage for each SCCmec coverage."""
    sccmec = {}
    for line in gziplines(coverage):
        line = line.rstrip()
        cassette, base, coverage = line.split('\t')

        if cassette not in sccmec:
            sccmec[cassette] = {
                'coverage': [],
                'total': 0
            }

        if int(coverage):
            sccmec[cassette]['total'] += 1

        sccmec[cassette]['coverage'].append(int(coverage))

    return sccmec
