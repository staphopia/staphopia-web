"""API utilities for resistance related viewsets."""
from collections import OrderedDict
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
        if row['results']:
            for i in row['results']:
                result = {}
                result['sample_id'] = row['sample_id']
                for key, val in i.items():
                    if key == 'cluster_id':
                        r_class = cluster[val]['resistance_class']
                        result['resistance_class'] = r_class
                        result['mechanism'] = cluster[val]['mechanism']
                        result['ref_name'] = cluster[val]['ref_name']
                        result['database'] = cluster[val]['database']
                        result['headers'] = cluster[val]['headers']
                    result[key] = val
                results.append(result)
    return results


def get_ariba_resistance_report(sample_id, user_id):
    """Return resistance report based on class associated with a sample."""
    resistance_class = []
    cluster = {}
    sql = """SELECT id, name FROM resistance_resistanceclass ORDER BY name"""
    for row in query_database(sql):
        cluster[row['id']] = row
        if row['name'].title() not in resistance_class:
            if row['name'] == 'MLS':
                resistance_class.append(row['name'])
            else:
                resistance_class.append(row['name'].title())

    sql = """SELECT sample_id, summary
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
        sample = OrderedDict()
        sample['sample_id'] = row['sample_id']
        for c in resistance_class:
            sample[c] = False

        for r in row['summary']:
            rclass = r['resistance_class']
            if rclass == 'MLS':
                sample[rclass] = True
            else:
                sample[rclass.title()] = True

        results.append(sample)

    return results


def get_ariba_resistance_summary(sample_id, user_id):
    """Return resistance summary based on class associated with a sample."""
    sql = """SELECT sample_id, summary
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
        for r in row['summary']:
            sample = OrderedDict()
            sample['sample_id'] = row['sample_id']
            for key, val in r.items():
                sample[key] = val
            results.append(sample)

    return results
