"""API utilities for Sequencing related viewsets."""
from api.utils import query_database


def get_sequencing_stats(sample_id, user_id, is_original='FALSE',
                         qual_per_base=False, read_lengths=False):
    """Return sequencing stats for a list of sampel ids."""
    cols = ['sample_id', 'is_original', 'rank', 'total_bp', 'coverage',
            'read_total', 'read_min', 'read_mean', 'read_std', 'read_median',
            'read_max', 'read_25th', 'read_75th', 'qual_mean', 'qual_std',
            'qual_median', 'qual_25th', 'qual_75th']

    if qual_per_base:
        cols.append('qual_per_base')
    if read_lengths:
        cols.append('read_lengths')

    sql = """SELECT {0}
             FROM sequence_stat AS a
             LEFT JOIN sample_sample AS s
             ON a.sample_id=s.id
             WHERE sample_id IN ({1}) AND (s.is_public=TRUE OR s.user_id={2})
                   AND is_original={3}
             ORDER BY sample_id;""".format(
        ','.join(cols),
        ','.join([str(i) for i in sample_id]),
        user_id,
        is_original
    )
    return query_database(sql)
