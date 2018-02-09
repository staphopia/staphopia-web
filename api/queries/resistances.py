"""API utilities for resistance related viewsets."""
from api.utils import query_database


def get_ariba_resistance(sample_id, user_id):
    """Return resistance results associated with a sample."""
    cluster = {}
    sql = """SELECT * FROM resistance_cluster"""
    for row in query_database(sql):
        cluster[row['id']] = row

    sql = """SELECT sample_id, results
             FROM resistance_ariba AS r
             LEFT JOIN sample_sample AS s
             ON r.sample_id=s.id
             WHERE r.sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY r.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    results = []
    for row in query_database(sql):
        for result in row['results']:
            clid = result['cluster']
            result['sample_id'] = row['sample_id']
            result['cluster_name'] = cluster[clid]['name']
            result['resistance_class'] = cluster[clid]['resistance_class']
            result['mechanism'] = cluster[clid]['mechanism']
            result['ref_name'] = cluster[clid]['ref_name']
            result['database'] = cluster[clid]['database']
            result['headers'] = cluster[clid]['headers']
            results.append(result)
    return results
