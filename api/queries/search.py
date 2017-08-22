"""API utilities for search related queries."""
from api.utils import query_database, sanitized_query


def basic_search(q, is_public=True, cols=None, all_samples=False,
                 order_by='sample_id', direction='ASC', limit="", offset=""):
    """Conduct a basic search on samples."""
    if not cols:
        cols = [
            'sample_id', 'is_paired', 'is_public', 'is_published', 'sample_tag',
            'username', 'contains_ena_metadata', 'study_accession', 'study_title',
            'study_alias', 'secondary_study_accession', 'sample_accession',
            'secondary_sample_accession', 'submission_accession',
            'experiment_accession', 'experiment_title', 'experiment_alias',
            'tax_id', 'scientific_name', 'instrument_platform', 'instrument_model',
            'library_layout', 'library_strategy', 'library_selection',
            'center_name', 'center_link', 'cell_line', 'collected_by', 'location',
            'country', 'region', 'coordinates', 'description',
            'environmental_sample', 'biosample_first_public', 'germline',
            'isolate', 'isolation_source', 'serotype', 'serovar', 'sex',
            'submitted_sex', 'strain', 'sub_species', 'tissue_type',
            'biosample_scientific_name', 'sample_alias', 'checklist',
            'biosample_center_name', 'environment_biome', 'environment_feature',
            'environment_material', 'project_name', 'host', 'host_status',
            'host_sex', 'submitted_host_sex', 'host_body_site',
            'investigation_type', 'sequencing_method', 'broker_name',
            'st_stripped', 'is_exact', 'rank']

    if limit:
        limit = "LIMIT {0}".format(limit)
    if offset:
        offset = "OFFSET {0}".format(offset)

    q = q.strip()
    if all_samples:
        sql = """SELECT {0}
                 FROM sample_summary
                 WHERE is_public=TRUE
                 ORDER BY {1} {2}
                 {3} {4};""".format(
            ",".join(cols), order_by, direction, limit, offset
        )
        return query_database(sql)
    else:

        q = " & ".join(q.split(' '))
        sql = """SELECT {0}
                 FROM sample_summary
                 WHERE document @@ to_tsquery('english', %s) AND
                       is_public=TRUE
                 ORDER BY {1} {2}
                 {3} {4};""".format(
            ",".join(cols), order_by, direction, limit, offset
        )
        return sanitized_query(sql, [q])

def get_filtered_count(q, all_samples=False):
    """Conduct a basic search on samples."""

    if all_samples:
        sql = """SELECT count(*)
                 FROM sample_summary
                 WHERE is_public=TRUE;"""
        return query_database(sql)[0]['count']
    else:
        q = " & ".join(q.split(' '))
        sql = """SELECT count(*)
                 FROM sample_summary
                 WHERE document @@ to_tsquery('english', %s) AND
                       is_public=TRUE;"""
        return sanitized_query(sql, [q])[0]['count']

def total_samples(is_public=True):
    """Get total number of samples."""
    sql = """SELECT count(*) FROM sample_summary WHERE is_public=TRUE;"""
    row = query_database(sql)
    return row[0]['count']



