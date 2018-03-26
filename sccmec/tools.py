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

from assembly.tools import get_contigs
from sccmec.models import Cassette, Coverage, Proteins, Primers, Subtypes
from staphopia.utils import gziplines, get_blast_query, read_json, timeit


@timeit
@transaction.atomic
def insert_sccmec(sample, version, files, force=False):
    if force:
        delete_sccmec(sample, version)

    # Get contigs associated with sample.
    contigs = {}
    for contig in get_contigs(sample, version):
        contigs[contig.spades] = contig

    insert_coverage(sample, version, files)
    insert_blast(sample, version, files['sccmec_primers'], Primers, contigs)
    insert_blast(sample, version, files['sccmec_proteins'], Proteins, contigs)
    insert_blast(sample, version, files['sccmec_subtypes'], Subtypes, contigs)


def delete_sccmec(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying SCCmec related results.')
    Coverage.objects.filter(sample=sample, version=version).delete()
    Proteins.objects.filter(sample=sample, version=version).delete()
    Primers.objects.filter(sample=sample, version=version).delete()
    Subtypes.objects.filter(sample=sample, version=version).delete()


@timeit
def read_coverage(coverage, mec_types):
    """Return the per-base coverage for each SCCmec coverage."""
    sccmec = {}
    for mec in mec_types:
        sccmec[mec] = {'coverage': [], 'per_base_coverage': {}, 'total': 0}

    for line in gziplines(coverage):
        cassette, position, coverage = line.rstrip().split('\t')
        coverage = int(coverage)
        position = int(position)
        if coverage:
            sccmec[cassette]['total'] += 1
            sccmec[cassette]['per_base_coverage'][position] = coverage
        sccmec[cassette]['coverage'].append(coverage)
    return sccmec


@timeit
@transaction.atomic
def insert_coverage(sample, version, files):
    """Insert per-base coverage for each SCCmec cassette into the database."""
    cassettes = {}
    for cassette in Cassette.objects.all():
        cassettes[cassette.header] = cassette
    coverage_objects = []
    sccmec = read_coverage(files['sccmec_coverage'], cassettes.keys())
    for mec_type, stats in sccmec.items():
        np_array = numpy.array(stats['coverage'])
        cassette = cassettes[mec_type]
        total = stats['total'] / cassette.length

        # mecA related
        start = cassette.meca_start - 1
        stop = cassette.meca_stop - 1
        meca_total = 0
        meca = sccmec[cassette.header]['coverage'][start:stop]
        for pos in meca:
            if int(pos):
                meca_total += 1

        meca_total = meca_total / cassette.meca_length if meca_total else 0.00
        meca_array = numpy.array(meca) if meca_total else None

        coverage_objects.append(Coverage(
            sample=sample,
            version=version,
            cassette=cassette,
            total=float(f'{total:.2f}'),
            minimum=min(stats['coverage']),
            median=numpy.median(np_array),
            mean=float(f'{numpy.mean(np_array):.2f}'),
            maximum=max(stats['coverage']),
            # mecA
            meca_total=float(f'{meca_total:.2f}'),
            meca_minimum=min(meca) if meca_total else 0,
            meca_median=numpy.median(meca_array) if meca_total else 0,
            meca_mean=(
                float(f'{numpy.mean(meca_array):.2f}') if meca_total else 0.00
            ),
            meca_maximum=max(meca) if meca_total else 0,
            per_base_coverage=json.dumps(stats['per_base_coverage'],
                                         sort_keys=True)
        ))

    try:
        Coverage.objects.bulk_create(coverage_objects, batch_size=500)
        print(f'{sample.name}: SCCmec coverages saved.')
    except IntegrityError as e:
        raise CommandError(f'{sample.name} SCCmec coverages Error: {e}')


@timeit
@transaction.atomic
def insert_blast(sample, version, blast, table, contigs):
    """."""
    hits = []
    json_data = read_json(blast)
    for entry in json_data['BlastOutput2']:
        hit = entry['report']['results']['search']
        if len(hit['hits']):
            # Filter results on a contig <= 200bp
            if hit['hits'][0]['description'][0]['title'] in contigs:
                # Get query and contig
                query = get_blast_query(hit['query_title'], hit['query_len'])
                contig = contigs[hit['hits'][0]['description'][0]['title']]

                # Only storing the top hit
                hsp = hit['hits'][0]['hsps'][0]

                # Includes mismatches and gaps
                mismatch = hsp['align_len'] - hsp['identity']

                # Hamming distance
                hd = mismatch
                if hit['query_len'] > hsp['align_len']:
                    # Include those bases that weren't aligned
                    hd = hit['query_len'] - hsp['align_len'] + mismatch

                hits.append(table(
                    sample=sample,
                    version=version,
                    contig=contig,
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
        table.objects.bulk_create(hits, batch_size=5000)
        print(f'{sample.name} SCCmec blast results saved.')
    except IntegrityError as e:
        raise CommandError(f'{sample.name} SCCmec blast result Error: {e}')


def max_primer_hamming_distance():
    return ({
        "IS1272-F": 20, "IS7": 24, "IS5": 23, "IS2": 25, "mecI-R": 19,
        "mecI-F": 21, "mI6": 23, "mI4": 20, "mI3": 25, "mecR1-R": 24,
        "mcR5": 21, "mcR3": 20, "mcR2": 20, "mA7": 23, "mA6": 18,
        "mA2": 21, "mA1": 21, "ccrCf-B": 27, "ccrCr-B": 28, "ccrCr-A": 22,
        "ccrCf-A": 20, "ccrB4": 20, "ccrB": 22, "ccrA4": 20, "ccrA3": 23,
        "ccrA2": 24, "ccrA1": 24
    })


def predict_type_by_primers(sample_id, blast_results, hamming_distance=False):
    sample_hits = OrderedDict()
    for sample in sorted(sample_id):
        sample_hits[int(sample)] = []

    for hit in blast_results:
        sample_hits[hit['sample_id']].append(hit)

    predictions = []
    # max_hamming = max_primer_hamming_distance()
    for sample, hits in sample_hits.items():
        dist = max_primer_hamming_distance()
        primers = OrderedDict()
        for key in dist:
            primers[key] = False

        for hit in hits:
            if '|' in hit['title']:
                name, primer = hit['title'].split('|')
            else:
                name = hit['title']

            # Differentiate the mec class primers
            if name in ['mecR1', 'mecI', 'mecA', 'IS1272', 'IS431']:
                name = primer
            elif name == 'ccrCf':
                if int(hit['length']) == 27:
                    name = 'ccrCf-B'
                else:
                    name = 'ccrCf-A'
            elif name == 'ccrCr':
                if int(hit['length']) == 28:
                    name = 'ccrCr-B'
                else:
                    name = 'ccrCr-A'

            dist[name] = int(hit['hamming_distance'])
            if int(hit['hamming_distance']) == 0:
                # Require perfect matches
                primers[name] = True

        # Determine ccrC
        dist['ccrC'] = min((dist['ccrCr-B'] + dist['ccrCf-B']),
                           (dist['ccrCr-A'] + dist['ccrCf-A']))
        if ((primers['ccrCr-B'] and primers['ccrCf-B']) or
                (primers['ccrCr-A'] and primers['ccrCf-A'])):
            primers['ccrC'] = True
        else:
            primers['ccrC'] = False

        # Determine mec class
        mec_class = {'meca': False, 'A': False, 'B': False, 'C': False,
                     'AB': False, 'ABC': False}
        mec_dist = {'meca': 0, 'A': 0, 'B': 0, 'C': 0, 'AB': 0, 'ABC': 0}

        if hamming_distance:
            mec_dist['meca'] = dist['mA1'] + dist['mA2']
            # Class A
            mec_dist['A'] = mec_dist['meca'] + min(
                (dist['mI4'] + dist['mI3'] + dist['mcR2'] + dist['mcR5']),
                (dist['mI4'] + dist['mcR3'])
            )

            # Class B
            mec_dist['B'] = mec_dist['meca'] + dist['IS5'] + dist['mA6']

            # Class C
            mec_dist['C'] = mec_dist['meca'] + dist['IS2']

            # Class A,B
            mec_dist['AB'] = (mec_dist['meca'] + dist['mecI-R'] +
                              dist['mecI-F'] + dist['IS1272-F'] +
                              dist['mecR1-R'])

            # Class A,B,C
            mec_dist['ABC'] = (mec_dist['meca'] + dist['mecI-R'] +
                               dist['mecI-F'] + dist['IS1272-F'] +
                               dist['mecR1-R'])

        # True/False Classes
        if primers['mA1'] and primers['mA2']:
            mec_class['meca'] = True
            # Class A
            if (primers['mI4'] and primers['mI3'] and primers['mcR2'] and
                    primers['mcR5']) or (primers['mI4'] and primers['mcR3']):
                    mec_class['A'] = True

            # Class B
            if primers['IS5'] and primers['mA6']:
                mec_class['B'] = True

            # Class C
            if primers['IS2']:
                mec_class['C'] = True

            # Class A,B
            if (primers['mecI-R'] and primers['mecI-F'] and
                    primers['IS1272-F'] and primers['mecR1-R']):
                mec_class['A'] = True
                mec_class['B'] = True
                mec_class['AB'] = True

            # Class A,B,C
            if (primers['mI6'] and primers['IS7'] and
                    primers['IS2'] and primers['mA7']):
                mec_class['A'] = True
                mec_class['B'] = True
                mec_class['C'] = True
                mec_class['ABC'] = True

        mec = OrderedDict([
            ('sample_id', sample),
            ('I', False), ('II', False), ('III', False), ('IV', False),
            ('V', False), ('VI', False), ('VII', False), ('VIII', False),
            ('IX', False), ('meca', mec_class['meca'])
        ])

        if hamming_distance:
            mec['meca'] = mec_dist['meca']
            mec['I'] = dist['ccrA1'] + dist['ccrB'] + mec_dist['B']
            mec['II'] = dist['ccrA2'] + dist['ccrB'] + mec_dist['A']
            mec['III'] = dist['ccrA3'] + dist['ccrB'] + mec_dist['A']
            mec['IV'] = dist['ccrA2'] + dist['ccrB'] + mec_dist['B']
            mec['V'] = dist['ccrC'] + mec_dist['C']
            mec['VI'] = dist['ccrA4'] + dist['ccrB4'] + mec_dist['B']
            mec['VII'] = dist['ccrC'] + mec_dist['C']
            mec['VIII'] = dist['ccrA4'] + dist['ccrB4'] + mec_dist['A']
            mec['IX'] = dist['ccrA1'] + dist['ccrB'] + mec_dist['C']
        else:
            if primers['ccrA1'] and primers['ccrB'] and mec_class['B']:
                mec['I'] = True

            if primers['ccrA2'] and primers['ccrB'] and mec_class['A']:
                mec['II'] = True

            if primers['ccrA3'] and primers['ccrB'] and mec_class['A']:
                mec['III'] = True

            if primers['ccrA2'] and primers['ccrB'] and mec_class['B']:
                mec['IV'] = True

            if primers['ccrC'] and mec_class['C']:
                mec['V'] = True

            if primers['ccrA4'] and primers['ccrB4'] and mec_class['B']:
                mec['VI'] = True

            if primers['ccrC'] and mec_class['C']:
                mec['VII'] = True

            if primers['ccrA4'] and primers['ccrB4'] and mec_class['A']:
                mec['VIII'] = True

            if primers['ccrA1'] and primers['ccrB'] and mec_class['C']:
                mec['IX'] = True

        predictions.append(mec)

    return predictions


def max_subtype_hamming_distance():
    return ({
        "ivh-r": 20, "ivh-f": 20, "ivg-r": 20, "ivg-f": 20, "ivd-r": 20,
        "ivd-f": 20, "ivce-r": 20, "ivce-f": 20, "ivbf-r": 20, "ivbf-f": 20,
        "iva-r": 20, "iva-f": 20, "iiia-3ab": 20, "iiia-3a1": 20,
        "iib-2b4": 22, "iib-2b3": 21, "iia-kdpB2": 22, "iia-kdpB1": 22,
        "ia-1a4": 21, "ia-1a3": 23
    })


def predict_subtype_by_primers(sample_id, blast_results,
                               hamming_distance=False):
    sample_hits = OrderedDict()
    for sample in sorted(sample_id):
        sample_hits[int(sample)] = []

    for hit in blast_results:
        sample_hits[hit['sample_id']].append(hit)

    predictions = []
    for sample, hits in sample_hits.items():
        dist = max_subtype_hamming_distance()
        primers = {}
        for key in dist:
            primers[key] = False

        for hit in hits:
            name = hit['title']
            if int(hit['hamming_distance']) == 0:
                primers[name] = True
            dist[name] = int(hit['hamming_distance'])

        subtypes = OrderedDict([
            ('sample_id', sample),
            ('Ia', False), ('IIa', False), ('IIb', False), ('IIIa', False),
            ('IVa', False), ('IVb', False), ('IVc', False), ('IVd', False),
            ('IVg', False), ('IVh', False),
        ])

        if hamming_distance:
            subtypes['Ia'] = dist['ia-1a3'] + dist['ia-1a4']
            subtypes['IIa'] = dist['iia-kdpB1'] + dist['iia-kdpB2']
            subtypes['IIb'] = dist['iib-2b3'] + dist['iib-2b4']
            subtypes['IIIa'] = dist['iiia-3a1'] + dist['iiia-3ab']
            subtypes['IVa'] = dist['iva-f'] + dist['iva-r']
            subtypes['IVb'] = dist['ivbf-f'] + dist['ivbf-r']
            subtypes['IVc'] = dist['ivce-f'] + dist['ivce-r']
            subtypes['IVd'] = dist['ivd-f'] + dist['ivd-r']
            subtypes['IVg'] = dist['ivg-f'] + dist['ivg-r']
            subtypes['IVh'] = dist['ivh-f'] + dist['ivh-r']
        else:
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

        predictions.append(subtypes)

    return predictions
