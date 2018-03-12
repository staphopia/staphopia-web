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
    """Return the ENA submissions by year."""
    results = []
    total = 0
    for row in query_database("SELECT * FROM submission_by_year"):
        total += int(row['count'])
        results.append({
            'year': int(row['year']),
            'count': int(row['count']),
            'overall': total
        })

    return results
