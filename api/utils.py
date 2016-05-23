"""API utilities shared accorss viewsets."""
from collections import OrderedDict

from django.db import connection


def format_results(results):
    """Format query results to be similar to Django Rest Framework output."""
    return OrderedDict((("count", len(results)), ("results", results)))


def query_database(sql):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def get_ids_in_bulk(table, ids):
    """Return information from a given table for a list of ids."""
    sql = "SELECT * FROM {0} WHERE id IN ({1});".format(
        table, ','.join([str(i) for i in ids])
    )
    return format_results(query_database(sql))


def get_gene_features_by_sample(sample_id):
    """Return genes associated with a sample."""
    sql = """SELECT * FROM gene_features WHERE sample_id={0};""".format(
        sample_id
    )
    return format_results(query_database(sql))


def get_indels_by_sample(sample_id):
    """Return indels associated with a sample."""
    sql = """SELECT * FROM variant_toindel WHERE sample_id={0};""".format(
        sample_id
    )
    return format_results(query_database(sql))


def get_samples_by_tag(tag_id):
    """Return sampels associated with a tag."""
    sql = """SELECT t.sample_id, s.user_id, s.db_tag, s.sample_tag,
                    s.is_paired, s.is_public, s.is_published, s.md5sum
             FROM sample_totag AS t
             LEFT JOIN sample_sample AS s
             ON t.sample_id=s.id
             WHERE t.tag_id={0};""".format(tag_id)
    return format_results(query_database(sql))


def get_sccmec_coverage_by_sample(sample_id):
    """Return indels associated with a sample."""
    sql = """SELECT * FROM sccmec_coverage WHERE sample_id={0};""".format(
        sample_id
    )
    return format_results(query_database(sql))


def get_snps_by_sample(sample_id):
    """Return snps associated with a sample."""
    sql = """SELECT * FROM variant_tosnp WHERE sample_id={0};""".format(
        sample_id
    )
    return format_results(query_database(sql))


def get_tags_by_sample(sample_id):
    """Return tags associated with a sample."""
    sql = """SELECT s.sample_id, s.tag_id, t.tag, t.comment
             FROM sample_totag AS s
             LEFT JOIN sample_tag AS t
             ON s.tag_id=t.id
             WHERE s.sample_id={0};""".format(sample_id)
    return format_results(query_database(sql))
