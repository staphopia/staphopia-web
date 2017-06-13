"""API utilities for MLST related viewsets."""
from api.utils import query_database


def get_unique_st_samples():
    """Return list of public ENA samples with a unique ST."""
    return query_database('SELECT * FROM unique_mlst_samples;')


def get_blast_sequence_type(sample_id, user_id):
    """Return BLAST MLST loci results associated with a sample."""
    sql = """SELECT m.sample_id, m.locus_name, m.locus_id, m.bitscore, m.slen,
                    m.length, m.gaps, m.mismatch, m.pident, m.evalue
             FROM mlst_blast AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE m.sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY m.sample_id ASC, m.locus_name ASC;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    return query_database(sql)


def get_srst2_sequence_type(sample_id, user_id):
    """Return SRST2 sequence type associated with a sample."""
    sql = """SELECT m.sample_id, m.st_original, m.st_stripped, m.is_exact,
                    m.arcc, m.aroe, m.glpf, m.gmk, m.pta, m.tpi, m.yqil,
                    m.mismatches, m.uncertainty, m.depth, m."maxMAF"
             FROM mlst_srst2 AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY m.sample_id;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    return query_database(sql)
