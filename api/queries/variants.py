"""API utilities for variant related viewsets."""
from collections import OrderedDict

from api.utils import query_database
from api.queries.samples import get_samples
from staphopia.utils import reverse_complement


def get_samples_by_indel(indel_id, user_id, bulk=False):
    sql = """SELECT indel_id, members, count
             FROM variant_indelmember
             WHERE indel_id IN ({0});""".format(
        ','.join([str(i) for i in indel_id])
    )

    results = []
    for row in query_database(sql):
        if bulk:
            for sample_id in row['members']:
                results.append({
                    "indel_id": row['indel_id'],
                    "sample_id": sample_id
                })
        else:
            if len(row['members']):
                results = get_samples(user_id, sample_ids=row['members'])
            break
    return results


def get_indels_by_sample(sample_id, user_id, annotation_id=None):
    """Return indels associated with a sample."""
    sql = None
    if annotation_id:
        sql = """SELECT v.sample_id, v.indel
                 FROM variant_variant AS v
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) AND
                       (s.is_public=TRUE OR s.user_id={1});""".format(
            ','.join([str(i) for i in sample_id]),
            user_id
        )
    else:
        sql = """SELECT v.sample_id, v.indel
                 FROM variant_variant AS v
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) AND
                       (s.is_public=TRUE OR s.user_id={1});""".format(
            ','.join([str(i) for i in sample_id]),
            user_id
        )

    rows = {}
    indel_id = []
    for row in query_database(sql):
        rows[row['sample_id']] = row['indel']
        indels = []
        for indel in row['indel']:
            indels.append(indel['indel_id'])
        indel_id = list(set(indel_id + list(indels)))

    indel_info = {}
    if annotation_id:
        sql = """SELECT *
                 FROM variant_indel
                 WHERE id IN ({0}) AND annotation_id={1}""".format(
            ','.join([str(i) for i in indel_id]), annotation_id
        )
    else:
        sql = "SELECT * FROM variant_indel WHERE id IN ({0})".format(
            ','.join([str(i) for i in indel_id])
        )
    for row in query_database(sql):
        indel_info[row['id']] = row

    results = []
    for sample, indels in rows.items():
        for indel in indels:
            indel_id = int(indel['indel_id'])
            if indel_id in indel_info:
                results.append(OrderedDict([
                    ('sample_id', sample),
                    ('indel_id', indel_id),
                    ('annotation_id', indel['annotation_id']),
                    ('reference_position',
                     indel_info[indel_id]['reference_position']),
                    ('reference_base', indel_info[indel_id]['reference_base']),
                    ('alternate_base', indel_info[indel_id]['alternate_base']),
                    ('is_deletion', indel_info[indel_id]['is_deletion']),
                    ('feature_id', indel_info[indel_id]['feature_id']),
                    ('reference_id', indel_info[indel_id]['reference_id']),
                    ('AC', indel['AC'][0]),
                    ('GT', indel['GT'][0]),
                    ('AD', indel['AD'][0]),
                    ('GQ', indel['GQ'][0]),
                    ('AF', indel['AF'][0]),
                    ('MQ', indel['MQ'][0]),
                    ('PL', indel['PL'][0]),
                    ('DP', indel['DP'][0]),
                    ('QD', indel['QD'][0]),
                    ('quality', indel['quality']),
                    ('filter_id', indel['filter_id']),
                ]))
    return results


def get_samples_by_snp(snp_id, user_id, bulk=False):
    sql = """SELECT snp_id, members
             FROM variant_snpmember
             WHERE snp_id IN ({0});""".format(
        ','.join([str(i) for i in snp_id])
    )

    results = []
    for row in query_database(sql):
        if bulk:
            for sample_id in row['members']:
                results.append({
                    "snp_id": row['snp_id'],
                    "sample_id": sample_id
                })
        else:
            if len(row['members']):
                results = get_samples(user_id, sample_ids=row['members'])
            break
    return results

def get_snps_by_sample(sample_id, user_id, annotation_id=None):
    """Return snps associated with a sample."""
    sql = None
    if annotation_id:
        sql = """SELECT v.sample_id, v.snp
                 FROM variant_variant AS v
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) AND
                       (s.is_public=TRUE OR s.user_id={1});""".format(
            ','.join([str(i) for i in sample_id]),
            user_id
        )
    else:
        sql = """SELECT v.sample_id, v.snp
                 FROM variant_variant AS v
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) AND
                       (s.is_public=TRUE OR s.user_id={1});""".format(
            ','.join([str(i) for i in sample_id]),
            user_id
        )

    rows = {}
    snp_id = []
    for row in query_database(sql):
        rows[row['sample_id']] = row['snp']
        snps = []
        for snp in row['snp']:
            snps.append(snp['snp_id'])
        snp_id = list(set(snp_id + list(snps)))

    snp_info = {}
    if annotation_id:
        sql = """SELECT *
                 FROM variant_snp
                 WHERE id IN ({0}) AND annotation_id={1}""".format(
            ','.join([str(i) for i in snp_id]), annotation_id
        )
    else:
        sql = "SELECT * FROM variant_snp WHERE id IN ({0})".format(
            ','.join([str(i) for i in snp_id])
        )

    for row in query_database(sql):
        snp_info[row['id']] = row

    results = []
    for sample, snps in rows.items():
        for snp in snps:
            snp_id = int(snp['snp_id'])
            if snp_id in snp_info:
                results.append(OrderedDict([
                    ('sample_id', sample),
                    ('snp_id', snp_id),
                    ('annotation_id', snp['annotation_id']),
                    ('reference_position',
                     snp_info[snp_id]['reference_position']),
                    ('reference_base', snp_info[snp_id]['reference_base']),
                    ('alternate_base', snp_info[snp_id]['alternate_base']),
                    ('reference_codon', snp_info[snp_id]['reference_codon']),
                    ('alternate_codon', snp_info[snp_id]['alternate_codon']),
                    ('reference_amino_acid',
                     snp_info[snp_id]['reference_amino_acid']),
                    ('alternate_amino_acid',
                     snp_info[snp_id]['alternate_amino_acid']),
                    ('amino_acid_change',
                     snp_info[snp_id]['amino_acid_change']),
                    ('is_synonymous', snp_info[snp_id]['is_synonymous']),
                    ('is_transition', snp_info[snp_id]['is_transition']),
                    ('is_genic', snp_info[snp_id]['is_genic']),
                    ('feature_id', snp_info[snp_id]['feature_id']),
                    ('reference_id', snp_info[snp_id]['reference_id']),
                    ('AC', snp['AC'][0]),
                    ('GT', snp['GT'][0]),
                    ('AD', snp['AD'][0]),
                    ('GQ', snp['GQ'][0]),
                    ('AF', snp['AF'][0]),
                    ('MQ', snp['MQ'][0]),
                    ('PL', snp['PL'][0]),
                    ('DP', snp['DP'][0]),
                    ('QD', snp['QD'][0]),
                    ('quality', snp['quality']),
                    ('filter_id', snp['filter_id']),
                ]))

    return results


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


def get_reference_genome_sequence(reference_id):
    """Return snps associated with a sample."""
    sql = """SELECT position, base
             FROM variant_referencegenome
             WHERE reference_id={0}
             ORDER BY position;""".format(
        reference_id
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


def get_annotation_strand(annotation_ids):
    """Get the strand info for a set of annotation ids."""
    sql = """SELECT id, strand FROM variant_annotation
             WHERE id IN ({0});""".format(
        ','.join([str(i) for i in annotation_ids])
    )

    return query_database(sql)


def get_snps_by_annotation(annotation_ids):
    """Get SNP IDs associated with a given Annotation IDs."""
    sql = """SELECT id, reference_position, reference_base, alternate_base,
                    annotation_id
             FROM variant_snp
             WHERE annotation_id IN ({0})
             ORDER BY reference_position ASC""".format(
        ','.join([str(i) for i in annotation_ids])
    )

    return query_database(sql)


def get_representative_sequence(sample_ids, annotation_ids,
                                save_reference=True):
    """Return fasta formatted sequence."""
    # Get annotation info
    strand = {}
    for row in get_annotation_strand(annotation_ids):
        strand[row['id']] = row['strand']

    # Get snp_ids with annotation id
    snps = {}
    reference = OrderedDict()
    for row in get_snps_by_annotation(annotation_ids):
        reference[row['reference_position']] = {
            'base': row['reference_base'].lower(),
            'annotation_id': row['annotation_id']
        }
        snps[row['id']] = {
            'reference_position': row['reference_position'],
            'alternate_base': row['alternate_base'],
        }

    # Get snp_ids in sample
    samples = OrderedDict()
    for sample in sample_ids:
        samples[sample] = {}

    if len(snps.keys()):
        sql = """SELECT sample_id, snp_id
                 FROM variant_tosnp
                 WHERE sample_id IN ({0}) AND snp_id IN ({1})
                 ORDER BY sample_id, snp_id ASC""".format(
            ','.join([str(i) for i in sample_ids]),
            ','.join([str(i) for i in snps.keys()])
        )
        for row in query_database(sql):
            if row['sample_id'] not in samples:
                samples[row['sample_id']] = {}

            position = snps[row['snp_id']]['reference_position']
            alternate_base = snps[row['snp_id']]['alternate_base']
            samples[row['sample_id']][position] = alternate_base

    # Substitute sequence
    sequences = OrderedDict()
    for sample, sample_snps in samples.items():
        annotation = None
        if save_reference:
            sequences['reference'] = OrderedDict()
        sequences[sample] = OrderedDict()
        for position, base in reference.items():
            if annotation != base['annotation_id']:
                annotation = base['annotation_id']
                if save_reference:
                    sequences['reference'][annotation] = []
                sequences[sample][annotation] = []

            if position in sample_snps:
                sequences[sample][annotation].append(sample_snps[position])
            else:
                sequences[sample][annotation].append(base['base'])

            if save_reference:
                sequences['reference'][annotation].append(base['base'])

    # Generate Sequences
    concatenated = []
    for sample, annotation in sequences.items():
        sequence = []
        for annotation_id, seq in annotation.items():
            if strand[annotation_id]:
                sequence.append(''.join(seq))
            else:
                sequence.append(''.join(reverse_complement(seq)))

        concatenated.append(OrderedDict([
            ('sample_id', sample),
            ('sequence', ''.join(sequence))
        ]))

    return concatenated
