"""API utilities for sample related viewsets."""
from api.utils import query_database


def get_samples(sample_id=None, sample_ids=None):
    """Return samples."""
    sql = None
    if sample_id:
        sql = """SELECT s.id, s.sample_tag, s.is_paired, s.is_public, s.md5sum,
                        s.user_id, m.st_original, m.st_stripped,
                        m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id
                 WHERE s.id={0}""".format(sample_id)
    elif sample_ids:
        sql = """SELECT s.id, s.sample_tag, s.is_paired, s.is_public, s.md5sum,
                        s.user_id, m.st_original, m.st_stripped,
                        m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id
                 WHERE s.id IN ({0})""".format(
                ','.join([str(i) for i in sample_ids])
                )
    else:
        sql = """SELECT s.id, s.sample_tag, s.is_paired, s.is_public, s.md5sum,
                        s.user_id, m.st_original, m.st_stripped,
                        m.is_exact AS st_is_exact_match
                 FROM sample_sample as s
                 LEFT JOIN mlst_srst2 as m
                 ON s.id = m.sample_id"""

    return query_database(sql)


def get_samples_by_tag(tag_id):
    """Return samples associated with a tag."""
    sql = """SELECT t.sample_id, s.user_id, s.sample_tag,
                    s.is_paired, s.is_public, s.is_published,
                    m.st_original, m.st_stripped,
                    m.is_exact AS st_is_exact_match
             FROM sample_totag AS t
             LEFT JOIN sample_sample AS s
             ON t.sample_id=s.id
             LEFT JOIN mlst_srst2 as m
             ON m.sample_id=s.id
             WHERE t.tag_id={0}
             ORDER BY s.sample_tag ASC;""".format(tag_id)
    return query_database(sql)


def get_public_samples(is_published=False):
    """Return sample info associated with a tag."""
    sql = None
    if is_published:
        sql = 'SELECT * FROM published_ena_samples;'
        results = {}
        for row in query_database(sql):
            if row['sample_tag'] not in results:
                results[row['sample_tag']] = row
                if row['pmid']:
                    results[row['sample_tag']]['pmid'] = [int(row['pmid'])]
                else:
                    results[row['sample_tag']]['pmid'] = []
            else:
                if row['pmid']:
                    results[row['sample_tag']]['pmid'].append(int(row['pmid']))

        return [vals for k, vals in results.items()]

    else:
        return query_database('SELECT * FROM public_ena_samples;')


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


def get_tags_by_sample(sample_id):
    """Return tags associated with a sample."""
    sql = """SELECT s.sample_id, s.tag_id, t.tag, t.comment
             FROM sample_totag AS s
             LEFT JOIN sample_tag AS t
             ON s.tag_id=t.id
             WHERE s.sample_id={0};""".format(sample_id)
    return query_database(sql)
