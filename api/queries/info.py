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
             WHERE s.is_public=TRUE
             ORDER BY first_public;"""
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


def get_rank_by_year(is_original=False):
    """Return the published submissions by year."""
    results = []
    name = 'original' if is_original else 'cleanup'

    sql = """SELECT metadata->'first_public' AS first_public, rank
             FROM sample_metadata AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             LEFT JOIN sequence_summary AS t
             ON m.sample_id=t.sample_id
             LEFT JOIN sequence_stage AS u
             ON t.stage_id=u.id
             WHERE s.is_public=TRUE AND u.name='{0}'
                   AND s.is_flagged = FALSE
             ORDER BY first_public;""".format(
        name
    )

    years = {}
    overall = [0, 0, 0]
    for row in query_database(sql):
        year = int(row['first_public'][0:4])
        if year not in years:
            years[year] = {'bronze': 0, 'silver': 0, 'gold': 0, 'total': 0}

        if row['rank']:
            if row['rank'] == 1:
                years[year]['bronze'] += 1
            elif row['rank'] == 2:
                years[year]['silver'] += 1
            elif row['rank'] == 3:
                years[year]['gold'] += 1

            years[year]['total'] += 1

    overall = [0, 0, 0, 0]
    for key, val in sorted(years.items()):
        overall[0] += val['bronze']
        overall[1] += val['silver']
        overall[2] += val['gold']
        overall[3] += val['total']
        results.append({
            'year': key,
            'bronze': val['bronze'],
            'silver': val['silver'],
            'gold': val['gold'],
            'count': val['total'],
            'overall_bronze': overall[0],
            'overall_silver': overall[1],
            'overall_gold': overall[2],
            'overall': overall[3]
        })

    return results


def get_st_by_year():
    """Return the published submissions by year."""
    results = []
    sql = """SELECT metadata->'first_public' AS first_public, st
             FROM sample_metadata AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             LEFT JOIN mlst_mlst AS t
             ON m.sample_id=t.sample_id
             WHERE s.is_public=TRUE AND s.is_flagged = FALSE
             ORDER BY first_public;"""

    years = {}
    types = set()
    for row in query_database(sql):
        year = int(row['first_public'][0:4])
        if year not in years:
            years[year] = {'unique': [], 'novel': [], 'assigned': 0,
                           'unassigned': 0, 'total': 0}

        if row['st']:
            if row['st'] not in types:
                years[year]['novel'].append(row['st'])
                types.add(row['st'])
            years[year]['unique'].append(row['st'])
            years[year]['assigned'] += 1
        else:
            years[year]['unassigned'] += 1
        years[year]['total'] += 1

    overall = [0, 0, 0, 0]
    for key, val in sorted(years.items()):
        total_unique = len(list(set(val['unique'])))
        total_novel = len(list(set(val['novel'])))
        overall[0] += total_novel
        overall[1] += val['assigned']
        overall[2] += val['unassigned']
        overall[3] += val['total']
        results.append({
            'year': key,
            'unique': total_unique,
            'novel': total_novel,
            'assigned': val['assigned'],
            'unassigned': val['unassigned'],
            'count': val['total'],
            'overall_novel': overall[0],
            'overall_assigned': overall[1],
            'overall_unassigned': overall[2],
            'overall': overall[3]
        })

    return results
