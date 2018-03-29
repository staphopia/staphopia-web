"""API utilities for publication related viewsets."""
from api.utils import query_database


def get_pmids(sample_id, user_id):
    """Return publication results associated with a sample."""
    sql = """SELECT s.sample_id, q.pmid
             FROM sample_basic AS s
             LEFT JOIN publication_tosample AS p
             ON p.sample_id=s.sample_id
             LEFT JOIN publication_publication as q
             ON p.publication_id=q.id
             WHERE s.sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY s.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    results = []
    for row in query_database(sql):
        if row['pmid']:
            results.append({
                'sample_id': row['sample_id'],
                'pmid': row['pmid']
            })
    return results


def get_publications(pmid):
    """Return publication results associated with a pmid."""
    sql = None
    if pmid:
        sql = """SELECT pmid, authors, title, abstract, reference_ids, keywords
                 FROM publication_publication
                 WHERE pmid IN ({0})
                 ORDER BY pmid ASC;""".format(
            ','.join([str(i) for i in pmid])
        )
    else:
        sql = """SELECT pmid, authors, title, abstract, reference_ids, keywords
                 FROM publication_publication
                 ORDER BY pmid ASC;"""

    return query_database(sql)
