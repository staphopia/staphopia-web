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
        cassette, position, coverage = line = line.rstrip().split('\t')
        if int(coverage):
            sccmec[cassette]['total'] += 1

        sccmec[cassette]['coverage'].append(int(coverage))
        sccmec[cassette]['per_base_coverage'][position] = coverage

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
            meca_minimum=min(meca) if meca_array else 0,
            meca_median=numpy.median(meca_array) if meca_array else 0,
            meca_mean=(
                float(f'{numpy.mean(meca_array):.2f}') if meca_array else 0.00
            ),
            meca_maximum=max(meca) if meca_array else 0,
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


def predict_type_by_primers(sample_id, blast_results):
    sample_hits = OrderedDict()
    for sample in sorted(sample_id):
        sample_hits[int(sample)] = []

    for hit in blast_results:
        sample_hits[hit['sample_id']].append(hit)

    predictions = []
    for sample, hits in sample_hits.items():
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

        for hit in hits:
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
            ('sample_id', sample),
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

        predictions.append(mec_types)

    return predictions


def predict_subtype_by_primers(sample_id, blast_results):
    sample_hits = OrderedDict()
    for sample in sorted(sample_id):
        sample_hits[int(sample)] = []

    for hit in blast_results:
        sample_hits[hit['sample_id']].append(hit)

    predictions = []
    for sample, hits in sample_hits.items():
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

        for hit in hits:
            name = hit['title'].split('|')[0]
            primers[name] = True

        subtypes = OrderedDict([
            ('sample_id', sample),
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

        predictions.append(subtypes)

    return predictions
