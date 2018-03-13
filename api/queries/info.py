"""API utilities for info related queries."""
from api.utils import query_database


def get_sequencing_stats_by_year(is_original=False):
    """Return sequencing stats by year sample was first public."""
    original = 'TRUE' if is_original else 'FALSE'
    sql = """SELECT * FROM sequencing_stats_by_year({0});""".format(original)
    return query_database(sql)


def get_assembly_stats_by_year(is_scaffolds=False, is_plasmids=False):
    """Return metadata associated with a sample."""
    scaffold = 'TRUE' if is_scaffolds else 'FALSE'
    plasmid = 'TRUE' if is_plasmids else 'FALSE'
    sql = """SELECT * FROM assembly_stats_by_year({0}, {1});""".format(
        scaffold, plasmid
    )
    return query_database(sql)


def get_submission_by_year():
    """Return the published submissions by year."""
    results = []
    sql = """SELECT metadata->'first_public' AS first_public, s.is_published
             FROM sample_metadata AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE s.is_public=TRUE;"""
    years = {}
    for row in query_database(sql):
        year = int(row['first_public'][0:4])
        if year not in years:
            years[year] = {'published': 0, 'unpublished': 0, 'total': 0}

        if row['is_published']:
            years[year]['published'] += 1
        else:
            years[year]['unpublished'] += 1

        years[year]['total'] += 1

    overall = [0, 0, 0]
    for key, val in sorted(years.items()):
        overall[0] += val['published']
        overall[1] += val['unpublished']
        overall[2] += val['total']
        results.append({
            'year': key,
            'published': val['published'],
            'unpublished': val['unpublished'],
            'count': val['total'],
            'overall_published': overall[0],
            'overall_unpublished': overall[1],
            'overall': overall[2]
        })

    return results
