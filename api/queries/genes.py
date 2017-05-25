"""API utilities for gene related viewsets."""
from api.constants import COLUMNS

from api.utils import query_database


def get_genes_by_sample(sample_id, product_id=None, cluster_id=None):
    """Return genes associated with a sample."""
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
            WHERE g.sample_id={1} AND g.product_id={2}
            AND g.cluster_id={3};
        """.format(','.join(columns), sample_id, product_id, cluster_id)
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
            WHERE g.sample_id={1} AND g.product_id={2};
        """.format(','.join(columns), sample_id, product_id)
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
            WHERE g.sample_id={1} AND g.cluster_id={2};
        """.format(','.join(columns), sample_id, cluster_id)
    else:
        sql = """
            SELECT {0}
            FROM gene_features as g
            LEFT JOIN gene_product as p
            ON p.id = g.product_id
            LEFT JOIN gene_clusters as c
            ON c.id = g.cluster_id
            LEFT JOIN gene_referencemapping as a
            ON c.id = a.cluster_id
            WHERE g.sample_id={1};
        """.format(','.join(columns), sample_id)
    return query_database(sql)


def get_clusters_by_samples(ids):
    """Return genes associated with a sample."""
    columns = COLUMNS['gene_clusters']
    sql = """
        SELECT {0}
        FROM gene_features as g
        LEFT JOIN gene_product as p
        ON p.id = g.product_id
        LEFT JOIN gene_clusters as c
        ON c.id = g.cluster_id
        LEFT JOIN gene_referencemapping as a
        ON c.id = a.cluster_id
        WHERE sample_id IN ({1}) AND g."is_tRNA"=FALSE AND
              g."is_rRNA"=FALSE;
    """.format(','.join(columns), ','.join([str(i) for i in ids]))

    return query_database(sql)


def get_cluster_counts_by_samples(ids):
    """Return cluster counts associated with a set of samples."""
    sql = 'SELECT * FROM cluster_counts(ARRAY[{0}]);'.format(
        ','.join([str(i) for i in ids])
    )

    return query_database(sql)


def get_genes_by_samples(ids, product_id=None, cluster_id=None):
    """Return genes associated with a sample."""
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
            WHERE sample_id IN ({1}) AND product_id={2} AND cluster_id={3};
        """.format(','.join(columns), ','.join([str(i) for i in ids]),
                   product_id, cluster_id)
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
            WHERE sample_id IN ({1}) AND product_id={2};
        """.format(','.join(columns), ','.join([str(i) for i in ids]),
                   product_id)
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
            WHERE sample_id IN ({1}) AND cluster_id={2};
        """.format(','.join(columns), ','.join([str(i) for i in ids]),
                   cluster_id)
    else:
        sql = """
            SELECT {0}
            FROM gene_features as g
            LEFT JOIN gene_product as p
            ON p.id = g.product_id
            LEFT JOIN gene_clusters as c
            ON c.id = g.cluster_id
            LEFT JOIN gene_referencemapping as a
            ON c.id = a.cluster_id
            WHERE sample_id IN ({1});
        """.format(','.join(columns), ','.join([str(i) for i in ids]))
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
