"""API utilities for search related queries."""
from api.utils import query_database, sanitized_query


def basic_search(q, order_by='sample_id', direction='ASC', limit="",
                 offset=""):
    """Conduct a basic search on samples."""
    q = " & ".join(q.strip().split(' ')) if q else ''
    sql = """SELECT s.sample_id, name, is_published, st, rank,
                    metadata->'sample_accession' AS sample_accession,
                    metadata->'strain' AS strain,
                    metadata->'collection_date' AS collection_date,
                    metadata->'location' AS location,
                    metadata->'isolation_source' AS isolation_source
             FROM sample_basic AS s
             LEFT JOIN sample_metadata AS m
             ON s.sample_id=m.sample_id
             WHERE s.sample_id > 0 {0} USER_PERMISSION
             ORDER BY {1} {2}
             {3} {4};""".format(
        "AND document @@ to_tsquery('english', %s)" if q else '',
        order_by,
        direction,
        "LIMIT {0}".format(limit) if limit else '',
        "OFFSET {0}".format(offset) if offset else ''
    )

    results = []
    rank = {1: 'Bronze', 2: 'Silver', 3: 'Gold'}
    for row in sanitized_query(sql, [q]):
        row['rank'] = rank[row['rank']]
        results.append(row)
    return results


def get_filtered_count(q):
    """Conduct a basic search on samples."""
    q = " & ".join(q.strip().split(' ')) if q else ''
    sql = """SELECT count(*)
             FROM sample_basic  AS s
             LEFT JOIN sample_metadata AS m
             ON s.sample_id=m.sample_id
             WHERE s.sample_id > 0 {0} USER_PERMISSION;""".format(
        "AND document @@ to_tsquery('english', %s)" if q else ''
    )
    return sanitized_query(sql, [q])[0]['count']


def total_samples():
    """Get total number of samples."""
    sql = """SELECT count(*)
             FROM sample_basic
             WHERE sample_id > 0 USER_PERMISSION;"""
    return query_database(sql)[0]['count']
