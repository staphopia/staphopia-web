"""API utilities for sample related viewsets."""
from api.utils import query_database
from collections import OrderedDict


def get_samples(user_id, sample_id=None, sample_ids=None, user_only=False,
                st=False, name=False):
    """Return samples."""
    sql = None
    st_sql = ""
    if st:
        st_sql = f'AND m.st={st}'

    if user_only:
        sql = """SELECT s.id AS sample_id, s.is_public, s.is_published, s.name,
                        m.st
                 FROM sample_sample as s
                 LEFT JOIN mlst_mlst as m
                 ON s.id = m.sample_id
                 WHERE s.user_id={0} {1}
                 ORDER BY s.id DESC""".format(user_id, st_sql)
    elif name:
        sql = """SELECT s.id AS sample_id, s.is_public, s.is_published, s.name,
                        m.st
                 FROM sample_sample as s
                 LEFT JOIN mlst_mlst as m
                 ON s.id = m.sample_id
                 WHERE s.name='{0}'
                       AND (s.is_public=TRUE OR s.user_id={1})""".format(
            name,
            user_id
        )
    elif sample_id:
        sql = """SELECT s.id AS sample_id, s.is_public, s.is_published, s.name,
                        m.st
                 FROM sample_sample as s
                 LEFT JOIN mlst_mlst as m
                 ON s.id = m.sample_id
                 WHERE s.id={0}
                       AND (s.is_public=TRUE OR s.user_id={1})""".format(
            sample_id,
            user_id
        )
    elif sample_ids:
        sql = """SELECT s.id AS sample_id, s.is_public, s.is_published, s.name,
                        m.st
                 FROM sample_sample as s
                 LEFT JOIN mlst_mlst as m
                 ON s.id = m.sample_id
                 WHERE s.id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
                 ORDER BY s.id""".format(
            ','.join([str(i) for i in sample_ids]),
            user_id
        )
    else:
        sql = """SELECT s.id AS sample_id, s.is_public, s.is_published, s.name,
                        m.st
                 FROM sample_sample as s
                 LEFT JOIN mlst_mlst as m
                 ON s.id = m.sample_id
                 WHERE (s.is_public=TRUE OR s.user_id={0}) {1}""".format(
            user_id, st_sql
        )

    return query_database(sql)


def get_samples_by_tag(tag_id):
    """Return samples associated with a tag."""
    sql = """SELECT t.sample_id, s.name, s.is_public, s.is_published, m.st
             FROM sample_totag AS t
             LEFT JOIN sample_sample AS s
             ON t.sample_id=s.id
             LEFT JOIN mlst_mlst as m
             ON m.sample_id=s.id
             WHERE t.tag_id={0}
             ORDER BY s.name ASC;""".format(tag_id)
    return query_database(sql)


def get_public_samples(is_published=False, include_location=False, limit=None):
    """Return sample info associated with a tag."""
    limit_sql = ""
    if limit:
        limit_sql = f'LIMIT {limit}'

    sql = None
    if is_published:
        sql = f'SELECT * FROM published_ena_samples {limit_sql};'
        results = {}
        for row in query_database(sql):
            if row['name'] not in results:
                results[row['name']] = row
                if row['pmid']:
                    results[row['name']]['pmid'] = [int(row['pmid'])]
                else:
                    results[row['name']]['pmid'] = []
            else:
                if row['pmid']:
                    results[row['name']]['pmid'].append(int(row['pmid']))

        return [vals for k, vals in results.items()]
    elif include_location:
        sql = """SELECT p.sample_id, is_public, is_published, name, st,
                        metadata->>'location' AS location,
                        metadata->>'region' AS region,
                        metadata->>'country' AS country
                 FROM public_ena_samples AS p
                 LEFT JOIN sample_metadata AS m
                 ON p.sample_id=m.sample_id {0}""".format(limit_sql)
        return query_database(sql)
    else:
        return query_database(f'SELECT * FROM public_ena_samples {limit_sql};')


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


def get_tags_by_sample(sample_id, user_id):
    """Return tags associated with a sample."""
    sql = """SELECT s.sample_id, s.tag_id, t.tag, t.comment
             FROM tag_tosample AS s
             LEFT JOIN tag_tag AS t
             ON s.tag_id=t.id
             LEFT JOIN sample_sample AS a
             ON s.sample_id=a.id
             WHERE s.sample_id={0}
                   AND (a.is_public=TRUE OR a.user_id={1});""".format(
        sample_id,
        user_id
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
