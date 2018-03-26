"""API utilities for XYZ related viewsets."""
from sccmec.tools import predict_type_by_primers, predict_subtype_by_primers

from api.utils import query_database


def get_sccmec_primers_by_sample(sample_id, user_id, is_subtypes=False,
                                 exact_hits=False, predict=False,
                                 hamming_distance=False):
    """Return SCCmec primer hits asscociated with a sample_id."""
    sql = """SELECT p.sample_id, b.title, b.length, p.bitscore, p.evalue,
                    p.identity, p.mismatch, p.gaps, p.hamming_distance,
                    p.query_from, p.query_to, p.hit_from, p.hit_to,
                    p.align_len, p.qseq, p.hseq, p.midline, p.contig_id
             FROM {0} AS p
             LEFT JOIN staphopia_blastquery AS b
             ON p.query_id=b.id
             LEFT JOIN sample_sample AS s
             ON p.sample_id=s.id
             WHERE p.sample_id IN ({1}) AND (s.is_public=TRUE OR s.user_id={2})
                   AND p.hamming_distance{3}0
             ORDER BY sample_id;""" .format(
        'sccmec_subtypes' if is_subtypes else 'sccmec_primers',
        ','.join([str(i) for i in sample_id]),
        user_id,
        '=' if exact_hits and not predict else '>='
    )

    if predict or hamming_distance:
        if is_subtypes:
            return predict_subtype_by_primers(
                sample_id,
                query_database(sql),
                hamming_distance=hamming_distance
            )
        else:
            return predict_type_by_primers(
                sample_id,
                query_database(sql),
                hamming_distance=hamming_distance
            )
    else:
        return query_database(sql)


def get_sccmec_proteins_by_sample(sample_id, user_id):
    """Return SCCmec protein hits asscociated with a sample_id."""
    sql = """SELECT p.sample_id, b.title, b.length, p.bitscore, p.evalue,
                    p.identity, p.mismatch, p.gaps, p.hamming_distance,
                    p.query_from, p.query_to, p.hit_from, p.hit_to,
                    p.align_len, p.qseq, p.hseq, p.midline, p.contig_id
             FROM sccmec_proteins AS p
             LEFT JOIN staphopia_blastquery AS b
             ON p.query_id=b.id
             LEFT JOIN sample_sample AS s
             ON p.sample_id=s.id
             WHERE p.sample_id IN ({0}) AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY sample_id;""" .format(
        ','.join([str(i) for i in sample_id]),
        user_id,
    )

    return query_database(sql)


def get_sccmec_coverage_by_sample(sample_id, user_id):
    """Return SCCmec coverages asscociated with a sample_id."""
    sql = """SELECT cov.sample_id, cas.name, cov.total, cov.minimum, cov.mean,
                    cov.median, cov.maximum, cov.meca_total, cov.meca_minimum,
                    cov.meca_mean, cov.meca_median, cov.meca_maximum,
                    cov.cassette_id
             FROM sccmec_coverage AS cov
             LEFT JOIN sccmec_cassette AS cas
             ON cov.cassette_id=cas.id
             LEFT JOIN sample_sample AS s
             ON cov.sample_id=s.id
             WHERE cov.sample_id IN ({0})
                   AND (s.is_public=TRUE OR s.user_id={1})
             ORDER BY cov.total DESC;""".format(
        ','.join([str(i) for i in sample_id]),
        user_id
    )
    return query_database(sql)
