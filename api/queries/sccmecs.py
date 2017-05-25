"""API utilities for XYZ related viewsets."""
from sccmec.tools import predict_type_by_primers, predict_subtype_by_primers

from api.utils import query_database


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
