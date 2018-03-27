"""API utilities for sample related viewsets."""
from api.utils import query_database
from collections import OrderedDict


def get_samples(user_id, sample_id=None, sample_ids=None, user_only=False,
                st=False, name=False):
    """Return samples."""
    sql = None
    st_sql = ""
    if st:
        st_sql = f'AND st={st}'

    if user_only:
        sql = """SELECT sample_id, name, is_public, is_published, st, rank
                 FROM sample_basic
                 WHERE s.user_id={0} {1}
                 ORDER BY s.id DESC""".format(user_id, st_sql)
    elif name:
        sql = """SELECT sample_id, name, is_public, is_published, st, rank
                 FROM sample_basic
                 WHERE s.name='{0}'
                       AND (is_public=TRUE OR user_id={1})""".format(
            name,
            user_id
        )
    elif sample_id:
        sql = """SELECT sample_id, name, is_public, is_published, st, rank
                 FROM sample_basic
                 WHERE sample_id={0}
                       AND (is_public=TRUE OR user_id={1})""".format(
            sample_id,
            user_id
        )
    elif sample_ids:
        sql = """SELECT sample_id, name, is_public, is_published, st, rank
                 FROM sample_basic
                 WHERE sample_id IN ({0}) AND (is_public=TRUE OR user_id={1})
                 ORDER BY sample_id""".format(
            ','.join([str(i) for i in sample_ids]),
            user_id
        )
    else:
        sql = """SELECT sample_id, name, is_public, is_published, st, rank
                 FROM sample_basic
                 WHERE (is_public=TRUE OR user_id={0}) {1}""".format(
            user_id, st_sql
        )

    return query_database(sql)


def get_public_samples(is_published=False, include_location=False, limit=None):
    """Return sample info associated with a tag."""
    limit_sql = ""
    if limit:
        limit_sql = f'LIMIT {limit}'

    table = 'public_ena_samples'
    if is_published:
        table = 'published_ena_samples'

    if include_location:
        sql = """SELECT p.sample_id, name, is_public, is_published, st, rank,
                        metadata->>'location' AS location,
                        metadata->>'region' AS region,
                        metadata->>'country' AS country
                 FROM {0} AS p
                 LEFT JOIN sample_metadata AS m
                 ON p.sample_id=m.sample_id {1}""".format(table, limit_sql)
        return query_database(sql)
    else:
        sql = """SELECT sample_id, name, is_public, is_published, st, rank
                 FROM {0} {1};""".format(table, limit_sql)
        return query_database(sql)


def get_resistance_by_samples(sample_ids, resistance_id=None):
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


def get_sample_metadata(sample_id, user_id):
    """Return metadata associated with a sample."""
    fields = []
    for row in query_database("SELECT field FROM sample_metadatafields;"):
        fields.append(row['field'])

    sql = """SELECT s.id AS sample_id, metadata
             FROM sample_sample as s
             LEFT JOIN sample_metadata as m
             ON s.id = m.sample_id
             WHERE s.id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY s.id""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    results = []
    for row in query_database(sql):
        if 'metadata' in row:
            result = OrderedDict()
            result['sample_id'] = row['sample_id']
            for field in sorted(fields):
                if field in row['metadata']:
                    result[field] = row['metadata'][field]
                else:
                    result[field] = ''
            results.append(result)

    return results
