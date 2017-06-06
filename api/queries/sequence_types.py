"""API utilities for MLST related viewsets."""
from api.utils import query_database


def get_unique_st_samples():
    """Return list of punlic ENA samples with a unique ST."""
    return query_database('SELECT * FROM unique_mlst_samples;')


def get_srst2_by_samples(sample_ids):
    """Return sequence type associated with a sample."""
    sql = """SELECT sample_id, st_original, st_stripped, is_exact,
                    arcc, aroe, glpf, gmk, pta, tpi, yqil, mismatches,
                    uncertainty, depth, "maxMAF"
             FROM mlst_srst2
             WHERE sample_id IN ({0})
             ORDER BY sample_id;""".format(
        ','.join([str(i) for i in sample_ids])
    )

    return query_database(sql)
