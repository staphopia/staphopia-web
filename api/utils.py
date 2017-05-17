"""API utilities shared accorss viewsets."""
from collections import OrderedDict

from django.db import connection

from api.constants import COLUMNS
from sccmec.tools import predict_type_by_primers, predict_subtype_by_primers


def format_results(results, time=None):
    """Format query results to be similar to Django Rest Framework output."""
    if time:
        return OrderedDict((
            ("took", time), ("count", len(results)), ("results", results)
        ))
    else:
        return OrderedDict((("count", len(results)), ("results", results)))


def query_database(sql):
    """Submit SQL query to the database."""
    cursor = connection.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    return [OrderedDict(zip(cols, row)) for row in cursor.fetchall()]


def get_ids_in_bulk(table, ids, id_col="id"):
    """Return information from a given table for a list of ids."""
    sql = "SELECT * FROM {0} WHERE {1} IN ({2});".format(
        table,
        id_col,
        ','.join([str(i) for i in ids])
    )
    return query_database(sql)


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


def get_kmer_by_string(kmer, samples=None):
    """Query kmer against Elasticsearch cluster."""
    import requests
    from kmer.partitions import PARTITIONS
    child = kmer[-7:]
    table = 'kmer_{0}'.format(PARTITIONS[child].lower())
    url = 'http://localhost:9200/{0}/kmer/{1}/'.format(table, kmer)
    r = requests.get(url)
    json = r.json()
    total = 0
    result = {"results": []}
    if json['found']:
        for sample in json['_source']['samples']:
            sample_id, count = sample.split('-')
            if samples:
                sample_id = int(sample_id.lstrip('0'))
                if sample_id in samples:
                    result['results'].append({
                        "sample_id": sample_id,
                        "count": count
                    })
                    total += 1
            else:
                # Get all samples, only for admins
                return {
                    "has_errors": "MISSING_SAMPLES",
                    "message": "kmer requests must include samples to query"
                }
        result["count"] = total
        return result
    else:
        return json


def get_kmer_by_partition(partition, kmers, samples):
    """Query kmer against Elasticsearch cluster."""
    import requests
    results = []
    url = 'http://localhost:9200/{0}/kmer/_mget/'.format(partition)
    r = requests.post(url, json={"ids": [kmers]})
    json = r.json()
    if json['docs']:
        for index in json["docs"]:
            if index["found"]:
                for sample in index['_source']['samples']:
                    sample_id, count = sample.split('-')
                    sample_id = int(sample_id.lstrip('0'))
                    if sample_id in samples:
                        results.append({
                            "kmer": index['_id'],
                            "sample_id": sample_id,
                            "count": count
                        })
    return results


def get_kmer_by_sequence(sequence, samples):
    """Query kmer against Elasticsearch cluster."""
    import requests
    from kmer.partitions import PARTITIONS
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    k = 31
    kmers = [sequence[i:i + k] for i in range(0, len(sequence)+1-k)]
    tables = {}
    for kmer in kmers:
        child = kmer[-7:]
        table = 'kmer_{0}'.format(PARTITIONS[child].lower())
        if table not in tables:
            tables[table] = []
        tables[table].append(kmer)

        # Reverse complement
        rc_kmer = ''.join(
            [complement[base] for base in kmer][::-1]
        )
        child = rc_kmer[-7:]
        table = 'kmer_{0}'.format(PARTITIONS[child].lower())
        if table not in tables:
            tables[table] = []
        tables[table].append(rc_kmer)

    results = []
    for key, vals in tables.iteritems():
        url = 'http://localhost:9200/{0}/kmer/_mget/'.format(key)
        vals = list(set(vals))
        r = requests.post(url, json={"ids": vals})
        json_data = r.json()
        if json_data['docs']:
            for index in json_data["docs"]:
                if index["found"]:
                    for sample in index['_source']['samples']:
                        sample_id, count = sample.split('-')
                        sample_id = int(sample_id.lstrip('0'))
                        if sample_id in samples:
                            results.append({
                                "kmer": index['_id'],
                                "sample_id": sample_id,
                                "count": count
                            })
    return results


def get_indels_by_sample(sample_id):
    """Return indels associated with a sample."""
    sql = """SELECT v.indel_id, i.reference_position, i.reference_base,
                    i.alternate_base, i.is_deletion, v.confidence,
                    i.annotation_id, i.feature_id, i.reference_id,
                    v.filters_id, v.sample_id
             FROM variant_toindel AS v
             LEFT JOIN variant_indel as i
             ON v.indel_id=i.id
             WHERE sample_id={0};""".format(
        sample_id
    )
    return query_database(sql)


def get_annotated_indels_by_sample(sample_id):
    """Return indels associated with a sample."""
    sql = """SELECT t.sample_id, t.indel_id, t.confidence, s.reference_position,
                    s.reference_base, s.alternate_base
             FROM variant_toindel AS t
             LEFT JOIN variant_indel as s
             ON t.indel_id=s.id
             WHERE sample_id={0}
             ORDER BY s.reference_position;""".format(
        sample_id
    )
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
                    s.is_paired, s.is_public, s.is_published
             FROM sample_totag AS t
             LEFT JOIN sample_sample AS s
             ON t.sample_id=s.id
             WHERE t.tag_id={0}
             ORDER BY s.sample_tag ASC;""".format(tag_id)
    return query_database(sql)


def get_sccmec_primers_by_sample(sample_id, exact_hits=False, predict=False):
    """Return SCCmec primer hits asscociated with a sample_id."""
    sql = None
    if exact_hits or predict:
        sql = """SELECT p.sample_id, s.title, s.length, p.bitscore, p.evalue,
                        p.identity, p.mismatch, p.gaps, p.hamming_distance,
                        p.query_from, p.query_to, p.hit_from, p.hit_to,
                        p.align_len, p.qseq, p.hseq, p.midline, p.contig_id,
                        p.program_id
                 FROM sccmec_primers AS p
                 LEFT JOIN staphopia_blastquery AS s
                 ON p.query_id=s.id
                 WHERE p.sample_id={0} AND
                       p.hamming_distance=0;""".format(sample_id)
    else:
        sql = """SELECT p.sample_id, s.title, s.length, p.bitscore, p.evalue,
                        p.identity, p.mismatch, p.gaps, p.hamming_distance,
                        p.query_from, p.query_to, p.hit_from, p.hit_to,
                        p.align_len, p.qseq, p.hseq, p.midline, p.contig_id,
                        p.program_id
                 FROM sccmec_primers AS p
                 LEFT JOIN staphopia_blastquery AS s
                 ON p.query_id=s.id
                 WHERE p.sample_id={0};""".format(sample_id)

    if predict:
        return predict_type_by_primers(query_database(sql), sample_id)
    else:
        return query_database(sql)


def get_sccmec_subtypes_by_sample(sample_id, exact_hits=False, predict=False):
    """Return SCCmec primer hits asscociated with a sample_id."""
    sql = None
    if exact_hits or predict:
        sql = """SELECT p.sample_id, s.title, s.length, p.bitscore, p.evalue,
                        p.identity, p.mismatch, p.gaps, p.hamming_distance,
                        p.query_from, p.query_to, p.hit_from, p.hit_to,
                        p.align_len, p.qseq, p.hseq, p.midline, p.contig_id,
                        p.program_id
                 FROM sccmec_subtypes AS p
                 LEFT JOIN staphopia_blastquery AS s
                 ON p.query_id=s.id
                 WHERE p.sample_id={0} AND
                       p.hamming_distance=0;""".format(sample_id)
    else:
        sql = """SELECT p.sample_id, s.title, s.length, p.bitscore, p.evalue,
                        p.identity, p.mismatch, p.gaps, p.hamming_distance,
                        p.query_from, p.query_to, p.hit_from, p.hit_to,
                        p.align_len, p.qseq, p.hseq, p.midline, p.contig_id,
                        p.program_id
                 FROM sccmec_subtypes AS p
                 LEFT JOIN staphopia_blastquery AS s
                 ON p.query_id=s.id
                 WHERE p.sample_id={0};""".format(sample_id)

    if predict:
        return predict_subtype_by_primers(query_database(sql), sample_id)
    else:
        return query_database(sql)


def get_sccmec_coverage_by_sample(sample_id):
    """Return SCCmec primer hits asscociated with a sample_id."""
    sql = """SELECT cas.name, cov.total, cov.minimum, cov.mean, cov.median,
                    cov.maximum, cov.meca_total, cov.meca_minimum,
                    cov.meca_mean, cov.meca_median, cov.meca_maximum,
                    cov.cassette_id, cov.sample_id
             FROM sccmec_coverage AS cov
             LEFT JOIN sccmec_cassette AS cas
             ON cov.cassette_id=cas.id
             WHERE cov.sample_id={0}
             ORDER BY cov.total DESC;""".format(sample_id)
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


def get_unique_st_samples():
    """Return list of punlic ENA sampels with a unique ST."""
    return query_database('SELECT * FROM unique_mlst_samples;')


def get_reference_genome_sequence(reference_id):
    """Return snps associated with a sample."""
    sql = """SELECT position, base
             FROM variant_referencegenome
             WHERE reference_id={0}
             ORDER BY position;""".format(
        reference_id
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


def get_annotated_snps_by_sample(sample_id):
    """Return snps associated with a sample."""
    sql = """SELECT t.sample_id, t.snp_id, t.confidence, s.reference_position,
                    s.reference_base, s.alternate_base
             FROM variant_tosnp AS t
             LEFT JOIN variant_snp as s
             ON t.snp_id=s.id
             WHERE sample_id={0}
             ORDER BY s.reference_position;""".format(
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


def get_srst2_by_samples(sample_ids):
    """Return sequence type associated with a sample."""
    sql = """SELECT sample_id, st_original, st_stripped, is_exact,
                    arcc, aroe, glpf, gmk, pta, tpi, yqil, mismatches,
                    uncertainty, depth, "maxMAF"
             FROM mlst_srst2
             WHERE sample_id IN ({0})
             ORDER BY sample_id;""".format(
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
