"""API utilities for variant related viewsets."""
from api.utils import query_database


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


def get_variant_counts_by_samples(sample_ids):
    """Return snps associated with a sample."""
    sql = """SELECT sample_id, snp, indel, (snp + indel) as total
             FROM variant_counts
             WHERE sample_id IN ({0});""".format(
        ','.join([str(i) for i in sample_ids])
    )

    return query_database(sql)
