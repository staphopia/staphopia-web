"""API utilities for MLST related viewsets."""
from collections import OrderedDict
import json
from api.utils import query_database


def get_unique_st_samples():
    """Return list of public ENA samples with a unique ST."""
    return query_database('SELECT * FROM unique_mlst_samples;')


def get_sequence_type(sample_id, user):
    """Return MLST loci results associated with a sample."""
    sql = """SELECT sample_id, st, ariba, mentalist, blast
             FROM mlst_mlst AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE m.sample_id IN ({0}) USER_PERMISSION
             ORDER BY m.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id])
    )

    return query_database(sql)


def get_mlst_blast_results(sample_id, user):
    """Return MLST loci results associated with a sample."""
    sql = """SELECT sample_id, blast
             FROM mlst_report AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE m.sample_id IN ({0}) USER_PERMISSION
             ORDER BY m.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id])
    )

    results = []
    for row in query_database(sql):
        result = OrderedDict()
        result['sample_id'] = row['sample_id']
        unassigned = 0
        for loci, vals in sorted(row['blast'].items()):
            allele = int(vals['sseqid'].split('.')[1])
            result[loci] = str(allele)
            if not allele:
                unassigned += 1
        result['unassigned'] = unassigned
        results.append(result)
    return results


def get_mlst_allele_matches(sample_id, user):
    """Return MLST loci results associated with a sample."""
    sql = """SELECT sample_id, st, d.blast, d.ariba, d.mentalist
             FROM mlst_mlst AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             LEFT JOIN mlst_support AS d
             ON m.support_id=d.id
             WHERE m.sample_id IN ({0}) USER_PERMISSION
             ORDER BY m.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id])
    )

    results = []
    for row in query_database(sql):
        results.append({
            'sample_id': row['sample_id'],
            'st': row['st'],
            'matches': max(row['blast'], row['mentalist'], row['ariba'])
        })
    return results


def get_cgmlst(sample_id, user):
    """Return cgMLST loci results associated with a sample."""
    sql = "SELECT id, name FROM cgmlst_loci;"
    loci = {}
    for row in query_database(sql):
        loci[str(row['id'])] = row['name']

    sql = """SELECT sample_id, mentalist
             FROM cgmlst_cgmlst AS m
             LEFT JOIN sample_sample AS s
             ON m.sample_id=s.id
             WHERE m.sample_id IN ({0}) USER_PERMISSION
             ORDER BY m.sample_id ASC;""".format(
        ','.join([str(i) for i in sample_id])
    )
    results = []
    for row in query_database(sql):
        cgmlst = OrderedDict()
        cgmlst['sample_id'] = row['sample_id']
        for k in sorted(row['mentalist'], key=lambda x: int(x)):
            # k = Loci, v = Allele
            cgmlst[loci[k]] = row['mentalist'][k]
        results.append(cgmlst)
    return results
