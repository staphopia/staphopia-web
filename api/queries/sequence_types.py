"""API utilities for MLST related viewsets."""
from api.utils import query_database


def get_unique_st_samples():
    """Return list of public ENA samples with a unique ST."""
    return query_database('SELECT * FROM unique_mlst_samples;')


def get_blast_sequence_type(sample_ids):
    """Return BLAST MLST loci results associated with a sample."""
    sql = """SELECT sample_id, locus_name, locus_id, bitscore, slen, length,
                    gaps, mismatch, pident, evalue
             FROM mlst_blast
             WHERE sample_id IN ({0})
             ORDER BY sample_id ASC, locus_name ASC;""".format(
        ','.join([str(i) for i in sample_ids])
    )

    return query_database(sql)


def get_srst2_sequence_type(sample_ids):
    """Return SRST2 sequence type associated with a sample."""
    sql = """SELECT sample_id, st_original, st_stripped, is_exact,
                    arcc, aroe, glpf, gmk, pta, tpi, yqil, mismatches,
                    uncertainty, depth, "maxMAF"
             FROM mlst_srst2
             WHERE sample_id IN ({0})
             ORDER BY sample_id;""".format(
        ','.join([str(i) for i in sample_ids])
    )

    return query_database(sql)
