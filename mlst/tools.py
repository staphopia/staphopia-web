"""
Useful functions associated with mlst.

To use:
from mlst.tools import UTIL1, UTIL2, etc...
"""
import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import file_exists, read_json, timeit

from mlst.models import SequenceTypes, MLST, Report


def read_table(table, header=True, sep='\t', ):
    names = None
    rows = []
    with open(table, 'r') as fh:
        for line in fh:
            cols = line.rstrip().split(sep)
            if header:
                names = cols
                header = False
            else:
                rows.append(dict(zip(names, cols)))

    if len(rows) == 1:
        return rows[0]
    else:
        return rows


@timeit
def parse_ariba(basic_report, detailed_report):
    '''
    Basic Ariba Report (tabs not spaces)
    ST  arcC    aroE    glpF    gmk pta tpi yqiL
    22  7   6   1   5   8   8   6
    '''
    basic_report = read_table(basic_report)
    basic_report['uncertainty'] = False
    if 'Novel' in basic_report['ST']:
        basic_report['ST'] = "10000"
    elif basic_report['ST'] == 'ND':
        basic_report['ST'] = 0
    elif basic_report['ST'].endswith('*'):
        # * indicates uncertainty in Ariba call
        basic_report['ST'] = basic_report['ST'].rstrip('*')
        basic_report['uncertainty'] = True

    '''
    Parse Detailed Report (tabs not spaces)
    gene    allele  cov pc  ctgs    depth   hetmin  hets
    arcC    7   100.0   100.0   1   51.2    .   .
    aroE    6   100.0   100.0   1   51.0    .   .
    glpF    1   100.0   100.0   1   36.7    .   .
    gmk 5   100.0   100.0   1   45.7    .   .
    pta 8   100.0   100.0   1   61.5    .   .
    tpi 8   100.0   100.0   1   47.9    .   .
    yqiL    6   100.0   100.0   1   52.6    .   .
    '''
    detailed_report = read_table(detailed_report)

    return [basic_report, detailed_report]


@timeit
def parse_mentalist(basic_report, tie_report, vote_report):
    '''
    Basic Mentalist Report (tabs not spaces)
    Sample  arcC    aroE    glpF    gmk pta tpi yqiL    ST  clonal_complex
    ERX1666310  7   6   1   5   8   8   6   22
    '''
    basic_report = read_table(basic_report)
    detailed_report = {
        'ties': read_table(tie_report),
        'votes': read_table(vote_report)
    }

    return [basic_report, detailed_report]


@timeit
def parse_blast(basic_report):
    detailed_report = None
    with open(basic_report, 'r') as fh:
        detailed_report = json.load(fh)

    basic_report = {
        'arcc': int(detailed_report['arcC']['sseqid'].split('.')[1]),
        'aroe': int(detailed_report['aroE']['sseqid'].split('.')[1]),
        'glpf': int(detailed_report['glpF']['sseqid'].split('.')[1]),
        'gmk': int(detailed_report['gmk']['sseqid'].split('.')[1]),
        'pta': int(detailed_report['pta']['sseqid'].split('.')[1]),
        'tpi': int(detailed_report['tpi']['sseqid'].split('.')[1]),
        'yqil': int(detailed_report['yqiL']['sseqid'].split('.')[1]),
    }

    # Determine ST based on hits
    try:
        st = SequenceTypes.objects.get(**basic_report)
        basic_report['ST'] = st.st
    except SequenceTypes.DoesNotExist:
        basic_report['ST'] = 0

    return [basic_report, detailed_report]


@timeit
@transaction.atomic
def insert_mlst(sample, version, results, force=False):
    '''Insert sequence type into database.'''
    st = {
        'st': 0,
        'ariba': int(results['ariba']['ST']) if results['ariba'] else 0,
        'blast': int(results['blast']['ST']),
        'mentalist': int(results['mentalist']['ST']),
    }

    # Overlap, three digits (ariba, mentalist, blast)
    # If all agree: 111
    ariba = results['ariba']
    if st['ariba'] == st['mentalist'] and st['mentalist'] == st['blast']:
        st['st'] = st['ariba']
    elif st['ariba'] == st['mentalist']:
        st['st'] = st['ariba']
    elif st['ariba'] == st['blast']:
        st['st'] = st['ariba']
    elif st['mentalist'] == st['blast']:
        st['st'] = st['mentalist']
    elif st['ariba'] and st['ariba'] != 10000 and not ariba['uncertainty']:
        # 10000 is 'Novel' as considered by Ariba
        # If there is uncertainty, don't call ST soley on Ariba. Previous
        # conditions had support from other methods.
        st['st'] = st['ariba']
    elif st['mentalist']:
        st['st'] = st['mentalist']

    try:
        if force:
            MLST.objects.update_or_create(
                sample=sample,
                version=version,
                defaults=st
            )
            print(f'Updated MLST calls for {sample.name}')
        else:
            MLST.objects.create(sample=sample, version=version, **st)
            print(f'Inserted MLST calls for {sample.name}')
    except IntegrityError as e:
        raise CommandError(e)


@timeit
@transaction.atomic
def insert_report(sample, version, reports, force=False):
    '''Insert detailed report of mlst calls into database.'''
    try:
        if force:
            Report.objects.update_or_create(
                sample=sample,
                version=version,
                defaults=reports
            )
            print(f'Updated MLST reports for {sample.name}')
        else:
            Report.objects.create(sample=sample, version=version, **reports)
            print(f'Inserted MLST reports for {sample.name}')
    except IntegrityError as e:
        raise CommandError(
            f'{sample.name} exists, will not update unless --force is used. {e}'
        )
