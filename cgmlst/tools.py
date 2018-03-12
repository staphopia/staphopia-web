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

from cgmlst.models import CGMLST, Report, Loci


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


def get_loci():
    """Get the CGMLST loci names."""
    loci = {}
    for l in Loci.objects.all():
        loci[l.name] = l.pk
    return loci


@transaction.atomic
def create_loci(name):
    return Loci.objects.create(name=name).pk


@timeit
@transaction.atomic
def insert_cgmlst(sample, version, files, force=False):
    """Insert mlst results and the reports."""
    if force:
        delete_cgmlst(sample, version)

    temp, report = parse_mentalist(
        files['cgmlst_mentalist'],
        files['cgmlst_mentalist_ties'],
        files['cgmlst_mentalist_votes']
    )

    loci = get_loci()
    cgmlst = {}
    for name, val in temp.items():
        if name in ['Sample', 'ST', 'clonal_complex']:
            pass
        else:
            if name not in loci:
                loci[name] = create_loci(name)
            cgmlst[int(loci[name])] = int(val)

    try:
        CGMLST.objects.create(sample=sample, version=version, mentalist=cgmlst)
        Report.objects.create(sample=sample, version=version, mentalist=report)
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'CGMLST: Insert error for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))


@transaction.atomic
def delete_cgmlst(sample, version):
    """Force update, so remove from table."""
    print(f'{sample.name}: Force used, emptying cgmlst related results.')
    CGMLST.objects.filter(sample=sample, version=version).delete()
    Report.objects.filter(sample=sample, version=version).delete()
