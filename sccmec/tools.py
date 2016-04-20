"""
Useful functions associated with sccmec.

To use:
from sccmec.tools import UTIL1, UTIL2, etc...
"""
import numpy

from django.core.management.base import CommandError
from django.db import transaction
from django.db.utils import IntegrityError

from assembly.tools import get_contig
from sccmec.models import (
    Cassette, Coverage, PerBaseCoverage, Proteins, Primers
)
from staphopia.utils import gziplines, get_blast_query, read_json, timeit
from sample.tools import get_program_id


@timeit
@transaction.atomic
def insert_sccmec_coverage(coverage, sample, force=False):
    """Insert per-base coverage for each SCCmec cassette into the database."""
    if force:
        print("\tForce used, emptying SCCmec Coverage related results.")
        Coverage.objects.filter(sample=sample).delete()
        print("\tForce used, emptying SCCmec PerBaseCoverage related results.")
        PerBaseCoverage.objects.filter(sample=sample).delete()

    sccmec = __read_coverage(coverage)
    per_base_coverage = []
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

        for i in range(len(stats['coverage'])):
            if stats['coverage'][i]:
                per_base_coverage.append(PerBaseCoverage(
                    sample=sample,
                    cassette=cassette,
                    position=i + 1,
                    coverage=stats['coverage'][i]
                ))

        try:
            meca_total = float(meca_total) / cassette.meca_length
            meca_array = numpy.array(meca)
        except:
            meca_total = 0.00
            meca_array = None

        try:
            coverage = Coverage.objects.create(
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
        except IntegrityError as e:
            raise CommandError('{0} SCCmec Coverage Error: {1}'.format(
                sample.sample_tag, e)
            )

        print('\tSCCmec cassette {0} coverage stats saved.'.format(mec_type))

    try:
        PerBaseCoverage.objects.bulk_create(per_base_coverage, batch_size=5000)
        print('\tSCCmec PerBaseCoverage saved.')
    except IntegrityError as e:
        raise CommandError('{0} SCCmec PerBaseCoverage Error: {1}'.format(
            sample.sample_tag, e)
        )


@timeit
@transaction.atomic
def insert_sccmec_blast(blast, sample, is_primers=True, force=True):
    """."""
    obj = Primers if is_primers else Proteins
    hits = []

    if force:
        print("\tForce used, emptying SCCmec blast related results.")
        obj.objects.filter(sample=sample).delete()

    json_data = read_json(blast)
    program = None
    for entry in json_data['BlastOutput2']:
        hit = entry['report']['results']['search']

        # Get contig id
        if len(hit['hits']):
            # Get program, query and contig id
            if not program:
                program = get_program_id(
                    entry['report']['program'],
                    entry['report']['version'],
                    'database:{0}'.format(
                        entry['report']['search_target']['db']
                    )
                )
            query = get_blast_query(hit['query_title'], hit['query_len'])
            contig = get_contig(sample,
                                hit['hits'][0]['description'][0]['title'])

            # Only storing the top hit
            hsp = hit['hits'][0]['hsps'][0]

            # Includes mismatches and gaps
            mismatch = hsp['align_len'] - hsp['identity']

            # Hamming distance
            hd = mismatch
            if hit['query_len'] > hsp['align_len']:
                # Include those bases that weren't aligned
                hd = hit['query_len'] - hsp['align_len'] + mismatch

            hits.append(obj(
                sample=sample,
                contig=contig,
                program=program,
                query=query,

                bitscore=int(hsp['bit_score']),
                evalue=hsp['evalue'],
                identity=hsp['identity'],
                mismatch=mismatch,
                gaps=hsp['gaps'],
                hamming_distance=hd,
                query_from=hsp['query_from'],
                query_to=hsp['query_to'],
                hit_from=hsp['hit_from'],
                hit_to=hsp['hit_to'],
                align_len=hsp['align_len'],

                qseq=hsp['qseq'],
                hseq=hsp['hseq'],
                midline=hsp['midline']
            ))

    try:
        obj.objects.bulk_create(hits, batch_size=5000)
        print('\tSCCmec {0} blast results saved.'.format(
            'Primers' if is_primers else 'Proteins'
        ))
    except IntegrityError as e:
        raise CommandError('{0} SCCmec {1} Error: {2}'.format(
            sample.sample_tag,
            'Primers' if is_primers else 'Proteins',
            e
        ))


def __read_coverage(coverage):
    """Return the per-base coverage for each SCCmec coverage."""
    sccmec = {}
    for line in gziplines(coverage):
        line = line.rstrip()
        cassette, position, coverage = line.split('\t')

        if cassette not in sccmec:
            sccmec[cassette] = {
                'coverage': [],
                'total': 0
            }

        if int(coverage):
            sccmec[cassette]['total'] += 1

        sccmec[cassette]['coverage'].append(int(coverage))

    return sccmec
