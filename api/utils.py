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


def get_ids_in_bulk(table, ids, id_col="id"):
    """Return information from a given table for a list of ids."""
    sql = "SELECT * FROM {0} WHERE {1} IN ({2});".format(
        table, id_col,  ','.join([str(i) for i in ids])
    )
    return query_database(sql)


def get_gene_features_by_sample(sample_id):
    """Return genes associated with a sample."""
    sql = """SELECT * FROM gene_features WHERE sample_id={0};""".format(
        sample_id
    )
    return query_database(sql)


def get_kmer_by_string(kmer):
    """Query kmer against Elasticsearch cluster."""
    import requests
    from kmer.partitions import PARTITIONS
    child = kmer[-7:]
    table = 'kmer_{0}'.format(PARTITIONS[child].lower())
    url = 'http://localhost:9200/{0}/kmer/{1}/'.format(table, kmer)
    r = requests.get(url)
    json = r.json()
    if json['found']:
        result = {"count": int(json['_source']['count']), "results": []}
        for sample in json['_source']['samples']:
            sample_id, count = sample.split('-')
            result['results'].append({
                "sample_id": sample_id.lstrip('0'),
                "count": count
            })
        return result
    else:
        return json


def get_indels_by_sample(sample_id):
    """Return indels associated with a sample."""
    sql = """SELECT * FROM variant_toindel WHERE sample_id={0};""".format(
        sample_id
    )
    return query_database(sql)


def get_resitance_by_samples(sample_ids, resistance_id=None):
    """Return snps associated with a sample."""
    optional = ""
    if resistance_id:
        optional = "AND resistance_id={0}".format(resistance_id)
    sql = """SELECT sample_id, value as mic, phenotype
             FROM sample_toresistance
             WHERE sample_id IN ({0}) {1};""".format(
        ','.join([str(i) for i in sample_ids]), optional
    )

    return query_database(sql)


def get_samples_by_tag(tag_id):
    """Return sampels associated with a tag."""
    sql = """SELECT t.sample_id, s.user_id, s.db_tag, s.sample_tag,
                    s.is_paired, s.is_public, s.is_published
             FROM sample_totag AS t
             LEFT JOIN sample_sample AS s
             ON t.sample_id=s.id
             WHERE t.tag_id={0}
             ORDER BY s.sample_tag ASC;""".format(tag_id)
    return query_database(sql)


def get_sccmec_coverage_by_sample(sample_id):
    """Return indels associated with a sample."""
    sql = """SELECT * FROM sccmec_coverage WHERE sample_id={0};""".format(
        sample_id
    )
    return query_database(sql)


def get_snps_by_sample(sample_id):
    """Return snps associated with a sample."""
    sql = """SELECT sample_id, snp_id, filters_id, comment_id
             FROM variant_tosnp
             WHERE sample_id={0}
             ORDER BY snp_id;""".format(
        sample_id
    )
    return query_database(sql)


def get_snps_by_samples(sample_ids):
    """Return snps associated with a sample."""
    sql = """SELECT sample_id, snp_id, filters_id, comment_id
             FROM variant_tosnp
             WHERE sample_id IN ({0})
             ORDER BY snp_id;""".format(
        ','.join([str(i) for i in sample_ids])
    )

    return query_database(sql)


def get_tags_by_sample(sample_id):
    """Return tags associated with a sample."""
    sql = """SELECT s.sample_id, s.tag_id, t.tag, t.comment
             FROM sample_totag AS s
             LEFT JOIN sample_tag AS t
             ON s.tag_id=t.id
             WHERE s.sample_id={0};""".format(sample_id)
    return query_database(sql)
