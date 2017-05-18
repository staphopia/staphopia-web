"""
Useful functions associated with sccmec.

To use:
from sccmec.tools import UTIL1, UTIL2, etc...
"""
import json
import numpy
from collections import OrderedDict

from django.core.management.base import CommandError
from django.db import transaction
from django.db.utils import IntegrityError

from assembly.tools import get_contig
from sccmec.models import Cassette, Coverage, Proteins, Primers, Subtypes
from staphopia.utils import gziplines, get_blast_query, read_json, timeit
from sample.tools import get_program_id


@timeit
@transaction.atomic
def insert_sccmec_coverage(coverage, sample, force=False, skip=False):
    """Insert per-base coverage for each SCCmec cassette into the database."""
    save = True
    if force:
        print("\tForce used, emptying SCCmec Coverage related results.")
        Coverage.objects.filter(sample=sample).delete()
    elif skip:
        try:
            Coverage.objects.get(sample=sample)
        except Coverage.MultipleObjectsReturned:
            print("\tSkip reloading existing SCCmec Coverage.")
            save = False
        except Coverage.DoesNotExist:
            pass

    if save:
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
                    meca_maximum=max(meca) if meca else 0,
                    per_base_coverage=json.dumps(stats['per_base_coverage'],
                                                 sort_keys=True)
                )
            except IntegrityError as e:
                raise CommandError('{0} SCCmec Coverage Error: {1}'.format(
                    sample.sample_tag, e)
                )

            print('\tSCCmec cassette {0} coverage stats saved.'.format(
                mec_type
            ))


@timeit
@transaction.atomic
def insert_sccmec_blast(blast, sample, is_primers=True, is_subtype=False,
                        force=True, skip=False):
    """."""
    obj = None
    name = ""
    if is_primers:
        obj = Primers
        name = "Primers"
    elif is_subtype:
        obj = Subtypes
        name = "Subtypes"
    else:
        obj = Proteins
        name = "Proteins"

    hits = []

    save = True
    if force:
        print("\tForce used, emptying SCCmec blast related results.")
        obj.objects.filter(sample=sample).delete()
    elif skip:
        try:
            obj.objects.get(sample=sample)
        except obj.MultipleObjectsReturned:
            print("\tSkip reloading existing SCCmec {0}.".format(name))
            save = False
        except obj.DoesNotExist:
            pass

    if save:
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
                'per_base_coverage': {},
                'total': 0
            }

        if int(coverage):
            sccmec[cassette]['total'] += 1

        sccmec[cassette]['coverage'].append(int(coverage))
        sccmec[cassette]['per_base_coverage'][position] = coverage

    return sccmec


def predict_type_by_primers(blast_results, sample_id):
    primers = {
        # ccr
        'ccrA1': False, 'ccrA2': False, 'ccrA3': False, 'ccrA4': False,
        'ccrB': False, 'ccrB4': False,
        'ccrC': False,

        # IS elements
        'IS431': False, 'IS1272': False,

        # mec
        'mecA': False, 'mecR1': False, 'mecI': False
    }

    for hit in blast_results:
        name = hit['title'].split('|')[0]
        primers[name] = True

    # Determine mec class
    mec_class = {'A': False, 'B': False, 'C': False}
    if primers['IS431'] and primers['mecA'] and primers['mecR1']:
        mec_class['C'] = True

        if primers['mecI']:
            mec_class['A'] = True
            mec_class['C'] = False

        if primers['IS1272']:
            mec_class['B'] = True
            mec_class['C'] = False

    mec_types = OrderedDict([
        ('sample_id', sample_id),
        ('I', False), ('II', False), ('III', False), ('IV', False),
        ('V', False), ('VI', False), ('VII', False), ('VIII', False),
        ('IX', False), ('X', False), ('XI', False)
    ])

    if primers['ccrA1'] and primers['ccrB'] and mec_class['B']:
        mec_types['I'] = True

    if primers['ccrA2'] and primers['ccrB'] and mec_class['A']:
        mec_types['II'] = True

    if primers['ccrA3'] and primers['ccrB'] and mec_class['A']:
        mec_types['III'] = True

    if primers['ccrA2'] and primers['ccrB'] and mec_class['B']:
        mec_types['IV'] = True

    if primers['ccrC'] and mec_class['C']:
        mec_types['V'] = True

    if primers['ccrA4'] and primers['ccrB4'] and mec_class['B']:
        mec_types['VI'] = True

    if primers['ccrC'] and mec_class['C']:
        mec_types['VII'] = True

    if primers['ccrA4'] and primers['ccrB4'] and mec_class['A']:
        mec_types['VIII'] = True

    if primers['ccrA1'] and primers['ccrB'] and mec_class['C']:
        mec_types['IX'] = True

    return [mec_types]


def predict_subtype_by_primers(blast_results, sample_id):
    primers = {
        'ia-1a3': False, 'ia-1a4': False,
        'iia-kdpB1': False, 'iia-kdpB2': False,
        'iib-2b3': False, 'iib-2b4': False,
        'iiia-3a1': False, 'iiia-3ab': False,
        'iva-f': False, 'iva-r': False,
        'ivbf-f': False, 'ivbf-r': False,
        'ivce-f': False, 'ivce-r': False,
        'ivd-f': False, 'ivd-r': False,
        'ivg-f': False, 'ivg-r': False,
        'ivh-f': False, 'ivh-r': False,
    }

    for hit in blast_results:
        name = hit['title'].split('|')[0]
        primers[name] = True

    subtypes = OrderedDict([
        ('sample_id', sample_id),
        ('Ia', False), ('IIa', False), ('IIb', False), ('IIIa', False),
        ('IVa', False), ('IVb', False), ('IVc', False), ('IVd', False),
        ('IVg', False), ('IVh', False),
    ])

    if primers['ia-1a3'] and primers['ia-1a4']:
        subtypes['Ia'] = True

    if primers['iia-kdpB1'] and primers['iia-kdpB2']:
        subtypes['IIa'] = True

    if primers['iib-2b3'] and primers['iib-2b4']:
        subtypes['IIb'] = True

    if primers['iiia-3a1'] and primers['iiia-3ab']:
        subtypes['IIIa'] = True

    if primers['iva-f'] and primers['iva-r']:
        subtypes['IVa'] = True

    if primers['ivbf-f'] and primers['ivbf-r']:
        subtypes['IVb'] = True

    if primers['ivce-f'] and primers['ivce-r']:
        subtypes['IVc'] = True

    if primers['ivd-f'] and primers['ivd-r']:
        subtypes['IVd'] = True

    if primers['ivg-f'] and primers['ivg-r']:
        subtypes['IVg'] = True

    if primers['ivh-f'] and primers['ivh-r']:
        subtypes['IVh'] = True

    return [subtypes]
