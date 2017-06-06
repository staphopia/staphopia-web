"""API utilities for MLST related viewsets."""
from api.utils import query_database


def get_sequencing_stats(sample_ids, is_original='FALSE', qual_per_base=False,
                         read_lengths=False):
    """Return list of punlic ENA sampels with a unique ST."""
    cols = ['sample_id', 'is_original', 'rank', 'total_bp', 'coverage',
            'read_total', 'read_min', 'read_mean', 'read_std', 'read_median',
            'read_max', 'read_25th', 'read_75th', 'qual_mean', 'qual_std',
            'qual_median', 'qual_25th', 'qual_75th']

    if qual_per_base:
        cols.append('qual_per_base')
    if read_lengths:
        cols.append('read_lengths')

    sql = """SELECT {0}
             FROM sequence_stat
             WHERE sample_id IN ({1}) AND is_original={2}
             ORDER BY sample_id;""".format(
        ','.join(cols),
        ','.join([str(i) for i in sample_ids]),
        is_original
    )
    return query_database(sql)
