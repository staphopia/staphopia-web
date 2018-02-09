"""API utilities for MLST related viewsets."""
from api.utils import query_database


def get_unique_st_samples():
    """Return list of public ENA samples with a unique ST."""
    return query_database('SELECT * FROM unique_mlst_samples;')


def get_sequence_type(sample_id, user_id):
    """Return BLAST MLST loci results associated with a sample."""
    sql = """SELECT sample_id, st, ariba, mentalist, blast
             FROM mlst_mlst AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE m.sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY m.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    return query_database(sql)
