"""API utilities for gene related viewsets."""
from api.utils import query_database

COLUMNS = {
    'gene_features': [
        'g.sample_id', 'a.annotation_id', 'g.start',
        'g.end', 'g.is_positive', 'g."is_tRNA"', 'g."is_rRNA"', 'g.phase',
        'g.prokka_id', 'g.dna', 'g.aa', 'g.cluster_id',
        'c.name AS cluster_name', 'g.contig_id', 'g.inference_id',
        'g.note_id', 'g.product_id', 'p.product',
    ],
    'gene_clusters': [
        'g.sample_id', 'g.cluster_id', 'g.product_id'
    ]
}


def get_genes_by_sample(sample_id, user_id, product_id=None, cluster_id=None):
    """Return genes associated with a sample."""
    sql = None
    columns = COLUMNS['gene_features']

    if product_id and cluster_id:
        sql = """SELECT {0}
                 FROM gene_features as g
                 LEFT JOIN gene_product as p
                 ON p.id = g.product_id
                 LEFT JOIN gene_clusters as c
                 ON c.id = g.cluster_id
                 LEFT JOIN gene_referencemapping as a
                 ON c.id = a.cluster_id
                 LEFT JOIN sample_sample as s
                 ON g.sample_id=s.id
                 WHERE g.sample_id IN ({1})
                       AND (s.is_public=TRUE OR s.user_id={2})
                       AND g.product_id={3}
                       AND g.cluster_id={4};""".format(
            ','.join(columns),
            ','.join([str(i) for i in sample_id]),
            user_id,
            product_id,
            cluster_id
        )
    elif product_id:
        sql = """SELECT {0}
                 FROM gene_features as g
                 LEFT JOIN gene_product as p
                 ON p.id = g.product_id
                 LEFT JOIN gene_clusters as c
                 ON c.id = g.cluster_id
                 LEFT JOIN gene_referencemapping as a
                 ON c.id = a.cluster_id
                 LEFT JOIN sample_sample as s
                 ON g.sample_id=s.id
                 WHERE g.sample_id IN ({1})
                       AND (s.is_public=TRUE OR s.user_id={2})
                       AND g.product_id={3};""".format(
            ','.join(columns),
            ','.join([str(i) for i in sample_id]),
            user_id,
            product_id
        )
    elif cluster_id:
        sql = """SELECT {0}
                 FROM gene_features as g
                 LEFT JOIN gene_product as p
                 ON p.id = g.product_id
                 LEFT JOIN gene_clusters as c
                 ON c.id = g.cluster_id
                 LEFT JOIN gene_referencemapping as a
                 ON c.id = a.cluster_id
                 LEFT JOIN sample_sample as s
                 ON g.sample_id=s.id
                 WHERE g.sample_id IN ({1})
                       AND (s.is_public=TRUE OR s.user_id={2})
                       AND g.cluster_id={3};""".format(
            ','.join(columns),
            ','.join([str(i) for i in sample_id]),
            user_id,
            cluster_id
        )
    else:
        sql = """SELECT {0}
                 FROM gene_features as g
                 LEFT JOIN gene_product as p
                 ON p.id = g.product_id
                 LEFT JOIN gene_clusters as c
                 ON c.id = g.cluster_id
                 LEFT JOIN gene_referencemapping as a
                 ON c.id = a.cluster_id
                 LEFT JOIN sample_sample as s
                 ON g.sample_id=s.id
                 WHERE g.sample_id IN ({1})
                       AND (s.is_public=TRUE OR s.user_id={2});""".format(
            ','.join(columns),
            ','.join([str(i) for i in sample_id]),
            user_id
        )
    return query_database(sql)


def get_clusters_by_samples(sample_id, user_id):
    """Return genes associated with a sample."""
    columns = COLUMNS['gene_clusters']
    sql = """SELECT {0}
             FROM gene_features as g
             LEFT JOIN gene_product as p
             ON p.id = g.product_id
             LEFT JOIN gene_clusters as c
             ON c.id = g.cluster_id
             LEFT JOIN gene_referencemapping as a
             ON c.id = a.cluster_id
             LEFT JOIN sample_sample as s
             ON g.sample_id=s.id
             WHERE sample_id IN ({1}) AND (s.is_public=TRUE OR s.user_id={2})
                                      AND g."is_tRNA"=FALSE;""".format(
        ','.join(columns),
        ','.join([str(i) for i in sample_id]),
        user_id
    )

    return query_database(sql)


def get_cluster_counts_by_samples(ids):
    """Return cluster counts associated with a set of samples."""
    sql = 'SELECT * FROM cluster_counts(ARRAY[{0}]);'.format(
        ','.join([str(i) for i in ids])
    )

    return query_database(sql)


def get_gene_feature(feature_id):
    """Return filtered gene features."""
    columns = COLUMNS['gene_features']
    sql = """
        SELECT {0}
        FROM gene_features as g
        LEFT JOIN gene_product as p
        ON p.id = g.product_id
        LEFT JOIN gene_clusters as c
        ON c.id = g.cluster_id
        LEFT JOIN gene_referencemapping as a
        ON c.id = a.cluster_id
        WHERE g.id={1};
    """.format(','.join(columns), feature_id)

    return query_database(sql)


def get_gene_features(product_id=None, cluster_id=None):
    """Return filtered gene features."""
    sql = None
    columns = COLUMNS['gene_features']

    if product_id and cluster_id:
        sql = """
            SELECT {0}
            FROM gene_features as g
            LEFT JOIN gene_product as p
            ON p.id = g.product_id
            LEFT JOIN gene_clusters as c
            ON c.id = g.cluster_id
            LEFT JOIN gene_referencemapping as a
            ON c.id = a.cluster_id
            WHERE g.product_id={1} AND g.cluster_id={2};
        """.format(','.join(columns), product_id, cluster_id)
    elif product_id:
        sql = """
            SELECT {0}
            FROM gene_features as g
            LEFT JOIN gene_product as p
            ON p.id = g.product_id
            LEFT JOIN gene_clusters as c
            ON c.id = g.cluster_id
            LEFT JOIN gene_referencemapping as a
            ON c.id = a.cluster_id
            WHERE g.product_id={1};
        """.format(','.join(columns), product_id)
    elif cluster_id:
        sql = """
            SELECT {0}
            FROM gene_features as g
            LEFT JOIN gene_product as p
            ON p.id = g.product_id
            LEFT JOIN gene_clusters as c
            ON c.id = g.cluster_id
            LEFT JOIN gene_referencemapping as a
            ON c.id = a.cluster_id
            WHERE  g.cluster_id={1};
        """.format(','.join(columns), cluster_id)
    return query_database(sql)


def get_gene_features_by_product(product_id):
    """Return genes associated with a sample."""
    sql = """SELECT * FROM gene_features WHERE product_id={0};""".format(
        product_id
    )
    return query_database(sql)
