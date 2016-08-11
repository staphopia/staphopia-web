"""
Useful functions associated with mlst.

To use:
from mlst.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import file_exists, read_json, timeit

from mlst.models import Blast, Srst2


@timeit
@transaction.atomic
def insert_mlst_blast(blast, sample, force=False):
    """Insert JSON formatted BLAST hits against MLST loci."""
    if force:
        print("\tForce used, emptying MLST BLAST related results.")
        Blast.objects.filter(sample=sample).delete()

    json_data = read_json(blast)
    for locus, results in json_data.items():
        locus_id = results['sseqid'].split('_')[1]
        try:
            blastn, created = Blast.objects.get_or_create(
                sample=sample,
                locus_name=locus,
                locus_id=locus_id,
                bitscore=float(results['bitscore']),
                slen=results['slen'],
                length=results['length'],
                gaps=results['gaps'],
                mismatch=results['mismatch'],
                pident=results['pident'],
                evalue=results['evalue']
            )
            print("\tBLASTN Results Saved")
        except IntegrityError as e:
            raise CommandError('{0} MLSTBlast Error: {1}'.format(
                sample.sample_tag, e)
            )


@timeit
@transaction.atomic
def insert_mlst_srst2(srst2, sample, force=False):
    """Insert SRST2 hits against MLST loci."""
    if force:
        print("\tForce used, emptying MLST SRST2 related results.")
        Srst2.objects.filter(sample=sample).delete()

    if file_exists(srst2):
        cols = None
        with open(srst2, 'r') as fh:
            fh.readline()
            cols = fh.readline().rstrip().split('\t')

        if not cols[0]:
            cols = ['0'] * 13

        if len(cols) == 12:
            cols.append('0')

        try:
            # 0:Sample  1:st    2:arcc  3:aroe  4:glpf  5:gmk_  6:pta_  7:tpi_
            # 8:yqil    9:mismatches    10:uncertainty  11:depth    12:maxMAF
            st_stripped, is_exact = determine_st(cols[1])

            Srst2.objects.create(
                sample=sample,
                st_original=cols[1],
                st_stripped=st_stripped,
                is_exact=is_exact,
                arcc=cols[2],
                aroe=cols[3],
                glpf=cols[4],
                gmk=cols[5],
                pta=cols[6],
                tpi=cols[7],
                yqil=cols[8],
                mismatches=cols[9],
                uncertainty=cols[10],
                depth=float(cols[11]),
                maxMAF=float("{0:.7f}".format(float(cols[12])))
            )
            print("\tSRST2 Results Saved")
        except IntegrityError as e:
            raise CommandError('{0} MLSTSrst2 Error: {1}'.format(
                sample.sample_tag, e
            ))


def determine_st(st):
    """Determine stipped vs exact match ST."""
    import re
    exact_st = re.compile('^(\d+)$')
    likely_st = re.compile('^(\d+)(.*)$')

    if exact_st.match(st):
        # Exact match
        return [int(st), True]
    elif likely_st.match(st):
        # Good idea, there is either mismatche(s) or uncertainity
        m = likely_st.match(st)
        return [m.group(1), False]
    else:
        # Unable to determine ST
        return [0, False]
