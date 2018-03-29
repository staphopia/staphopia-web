"""API utilities for virulence related viewsets."""
from api.utils import query_database


def get_ariba_virulence(sample_id, user_id):
    """Return virulence results associated with a sample."""
    cluster = {}
    sql = """SELECT * FROM virulence_cluster"""
    for row in query_database(sql):
        cluster[row['id']] = row

    sql = """SELECT sample_id, results
             FROM virulence_ariba AS r
             LEFT JOIN sample_sample AS s
             ON r.sample_id=s.id
             WHERE r.sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY r.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    results = []
    for row in query_database(sql):
        result = {}
        result['sample_id'] = row['sample_id']
        for r in row['results']:
            for key, val in r.items():
                if key == 'cluster':
                    result['cluster_name'] = cluster[val]['name']
                    result['ref_name'] = cluster[val]['ref_name']
                result[key] = val
            results.append(result)
    return results
