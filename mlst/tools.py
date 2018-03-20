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

from mlst.models import SequenceTypes, MLST, Report, Support


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


def parse_ariba(basic_report, detailed_report):
    '''
    Basic Ariba Report (tabs not spaces)
    ST  arcC    aroE    glpF    gmk pta tpi yqiL
    22  7   6   1   5   8   8   6
    '''
    basic_report = read_table(basic_report)
    basic_report['uncertainty'] = False
    predicted_novel = False
    if basic_report['ST'].endswith('*'):
        # * indicates uncertainty in Ariba call
        basic_report['ST'] = basic_report['ST'].rstrip('*')
        basic_report['uncertainty'] = True

    if 'Novel' in basic_report['ST']:
        basic_report['ST'] = 0
        if not basic_report['uncertainty']:
            predicted_novel = True
    elif basic_report['ST'] == 'ND':
        basic_report['ST'] = 0

    total_assigned = 0
    for key, val in basic_report.items():
        if key not in ['ST', 'uncertainty']:
            if val.endswith("*") or val == 'ND':
                pass
            elif int(val):
                total_assigned += 1

    if total_assigned == 7 and not int(basic_report['ST']):
        # See if loci pattern exists
        try:
            st = SequenceTypes.objects.get(
                arcc=int(basic_report['arcC']),
                aroe=int(basic_report['aroE']),
                glpf=int(basic_report['glpF']),
                gmk=int(basic_report['gmk']),
                pta=int(basic_report['pta']),
                tpi=int(basic_report['tpi']),
                yqil=int(basic_report['yqiL'])
            )
            basic_report['ST'] = st.st
        except SequenceTypes.DoesNotExist:
            if predicted_novel:
                basic_report['ST'] = 10000

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

    return [basic_report, detailed_report, total_assigned]


def parse_mentalist(basic_report, tie_report, vote_report):
    '''
    Basic Mentalist Report (tabs not spaces)
    Sample  arcC    aroE    glpF    gmk pta tpi yqiL    ST  clonal_complex
    ERX1666310  7   6   1   5   8   8   6   22
    '''
    basic_report = read_table(basic_report)
    total_assigned = 0
    if int(basic_report['ST']):
        total_assigned = 7
    else:
        for key, val in basic_report.items():
            if key not in ['Sample', 'ST', 'clonal_complex']:
                if int(val):
                    total_assigned += 1

    detailed_report = {
        'ties': read_table(tie_report),
        'votes': read_table(vote_report)
    }

    # Remove the ties
    total_assigned = total_assigned - len(detailed_report['ties'])
    if total_assigned == 7 and not int(basic_report['ST']):
        # See if loci pattern exists
        try:
            st = SequenceTypes.objects.get(
                arcc=int(basic_report['arcC']),
                aroe=int(basic_report['aroE']),
                glpf=int(basic_report['glpF']),
                gmk=int(basic_report['gmk']),
                pta=int(basic_report['pta']),
                tpi=int(basic_report['tpi']),
                yqil=int(basic_report['yqiL'])
            )
            basic_report['ST'] = st.st
        except SequenceTypes.DoesNotExist:
            basic_report['ST'] = 0

    return [basic_report, detailed_report, total_assigned]


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
    total_assigned = 0
    try:
        st = SequenceTypes.objects.get(**basic_report)
        basic_report['ST'] = st.st
        total_assigned = 7
    except SequenceTypes.DoesNotExist:
        for key, val in basic_report.items():
            if val:
                total_assigned += 1
        basic_report['ST'] = 0

    return [basic_report, detailed_report, total_assigned]


@timeit
def insert_mlst(sample, version, files, force=False):
    """Insert mlst results and the reports."""
    st = {'ariba': 0}
    report = {'ariba': 'empty'}
    ariba_assigned = 0
    if 'fastq_r2' in files:
        # Ariba only works on paired end reads
        st['ariba'], report['ariba'], ariba_assigned = parse_ariba(
            files['mlst_ariba_mlst_report'],
            files['mlst_ariba_details']
        )

    st['mentalist'], report['mentalist'], mentalist_assigned = parse_mentalist(
        files['mlst_mentalist'],
        files['mlst_mentalist_ties'],
        files['mlst_mentalist_votes']
    )

    st['blast'], report['blast'], blast_assigned = parse_blast(
        files['mlst_blastn']
    )

    novel = {
        'ariba': ariba_assigned,
        'mentalist': mentalist_assigned,
        'blast': blast_assigned
    }

    if force:
        delete_mlst(sample, version)

    insert_mlst_results(sample, version, st, novel)
    insert_report(sample, version, report)


@transaction.atomic
def delete_mlst(sample, version):
    print(f'Deleting MLST calls/reports for {sample.name}')
    Report.objects.filter(sample=sample, version=version).delete()
    MLST.objects.filter(sample=sample, version=version).delete()


@transaction.atomic
def insert_mlst_results(sample, version, results, novel):
    '''Insert sequence type into database.'''
    st = {
        'st': 0,
        'ariba': int(results['ariba']['ST']) if results['ariba'] else 0,
        'blast': int(results['blast']['ST']),
        'mentalist': int(results['mentalist']['ST']),
    }

    ariba = results['ariba']
    if st['ariba'] == st['mentalist'] and st['mentalist'] == st['blast']:
        st['st'] = st['ariba']
    elif st['ariba'] == st['mentalist'] and st['mentalist']:
        st['st'] = st['ariba']
    elif st['ariba'] == st['blast'] and st['blast']:
        st['st'] = st['ariba']
    elif st['mentalist'] == st['blast'] and st['mentalist']:
        st['st'] = st['mentalist']
    elif st['ariba'] and st['ariba'] != 10000 and not ariba['uncertainty']:
        # 10000 is 'Novel' as considered by Ariba
        # If there is uncertainty, don't call ST soley on Ariba. Previous
        # conditions had support from other methods.
        st['st'] = st['ariba']
    elif st['mentalist']:
        st['st'] = st['mentalist']
    elif st['blast']:
        st['st'] = st['blast']

    # If ST still not determined, check if predicted to be novel
    predicted_novel = False
    if not st['st']:
        if novel['blast'] == 7 or novel['mentalist'] == 7:
            predicted_novel = True
        elif st['ariba'] == 10000:
            predicted_novel = True

    # Get support
    ariba_support = novel['ariba']
    mentalist_support = novel['mentalist']
    blast_support = novel['blast']

    support = Support.objects.get_or_create(
        ariba=ariba_support, mentalist=mentalist_support, blast=blast_support
    )
    try:
        MLST.objects.create(
            sample=sample,
            version=version,
            predicted_novel=predicted_novel,
            support=support[0],
            **st
        )
        print(f'Inserted MLST calls for {sample.name}')
    except IntegrityError as e:
        raise CommandError(e)


@transaction.atomic
def insert_report(sample, version, reports):
    '''Insert detailed report of mlst calls into database.'''
    try:
        Report.objects.create(sample=sample, version=version, **reports)
        print(f'Inserted MLST reports for {sample.name}')
    except IntegrityError as e:
        raise CommandError(
            f'{sample.name} found, will not update unless --force is used. {e}'
        )
