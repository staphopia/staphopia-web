"""
Useful functions associated with mlst.

To use:
from mlst.tools import UTIL1, UTIL2, etc...
"""
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import file_exists

from mlst.models import Blast, Srst2


@transaction.atomic
def insert_mlst_blast(blast, sample):
    """Insert BLAST hits against MLST loci."""
    if file_exists(blast):
        with open(blast, 'r') as fh:
            for line in fh:
                line = line.rstrip()
                # 0:sseqid 1:bitscore 2:slen 3:length
                # 4:gaps 5:mismatch 6:pident 7:evalue
                if line:
                    cols = line.split('\t')
                    locus_name, locus_id = cols[0].split('-')
                    locus_name = locus_name.replace('_', '')

                    try:
                        blastn, created = Blast.objects.get_or_create(
                            sample=sample,
                            locus_name=locus_name,
                            locus_id=locus_id,
                            bitscore=int(float(cols[1])),
                            slen=cols[2],
                            length=cols[3],
                            gaps=cols[4],
                            mismatch=cols[5],
                            pident=cols[6],
                            evalue=cols[7]
                        )
                        print("BLASTN Results Saved")
                    except IntegrityError as e:
                        raise CommandError('{0} MLSTBlast Error: {1}'.format(
                            sample.sample_tag, e)
                        )


@transaction.atomic
def insert_mlst_srst2(srst2, sample):
    """Insert SRST2 hits against MLST loci."""
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
                maxMAF=float("{0:.7f}".format(cols[12]))
            )
            print("SRST2 Results Saved")
        except IntegrityError as e:
            raise CommandError('{0} MLSTSrst2 Error: {1}'.format(
                sample.sample_tag, e
            ))


def determine_st(self, st):
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
