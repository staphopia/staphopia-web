"""API utilities for variant related viewsets."""
from collections import OrderedDict

from api.utils import query_database
from staphopia.utils import reverse_complement


def get_indels_by_sample(sample_id, user_id, annotation_id=None):
    """Return indels associated with a sample."""
    sql = None
    if annotation_id:
        sql = """SELECT v.sample_id, v.indel_id, i.reference_position,
                        i.reference_base, i.alternate_base, i.is_deletion,
                        v.confidence, i.annotation_id, i.feature_id,
                        i.reference_id, v.filters_id
                 FROM variant_toindel AS v
                 LEFT JOIN variant_indel as i
                 ON v.indel_id=i.id
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) AND
                       (s.is_public=TRUE OR s.user_id={1}) AND
                       i.annotation_id={2}
                 ORDER BY v.sample_id ASC, v.indel_id ASC;""".format(
            ','.join([str(i) for i in sample_id]),
            user_id,
            annotation_id
        )
    else:
        sql = """SELECT v.sample_id, v.indel_id, i.reference_position,
                        i.reference_base, i.alternate_base, i.is_deletion,
                        v.confidence, i.annotation_id, i.feature_id,
                        i.reference_id, v.filters_id
                 FROM variant_toindel AS v
                 LEFT JOIN variant_indel as i
                 ON v.indel_id=i.id
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) AND
                      (s.is_public=TRUE OR s.user_id={1})
                 ORDER BY v.sample_id ASC, v.indel_id ASC;""".format(
            ','.join([str(i) for i in sample_id]),
            user_id
        )

    results = []
    for row in query_database(sql):
        confidence = row['confidence']
        results.append(OrderedDict([
            ('sample_id', row['sample_id']),
            ('indel_id', row['indel_id']),
            ('annotation_id', row['annotation_id']),
            ('reference_position', row['reference_position']),
            ('reference_base', row['reference_base']),
            ('alternate_base', row['alternate_base']),
            ('is_deletion', row['is_deletion']),
            ('feature_id', row['feature_id']),
            ('reference_id', row['reference_id']),
            ('AC', confidence['AC']),
            ('GT', confidence['GT']),
            ('AD', confidence['AD']),
            ('GQ', confidence['GQ']),
            ('AF', confidence['AF']),
            ('MQ', confidence['MQ']),
            ('PL', confidence['PL']),
            ('DP', confidence['DP']),
            ('QD', confidence['QD']),
            ('quality', confidence['quality']),
            ('filters_id', row['filters_id']),
        ]))
    return results


def get_snps_by_sample(sample_id, user_id, annotation_id=None):
    """Return snps associated with a sample."""
    sql = None
    if annotation_id:
        sql = """SELECT v.sample_id, v.snp_id, s.annotation_id,
                        s.reference_position, s.reference_base,
                        s.alternate_base,
                        s.reference_codon, s.alternate_codon,
                        s.reference_amino_acid, s.alternate_amino_acid,
                        s.amino_acid_change, s.is_synonymous, s.is_transition,
                        s.is_genic, v.confidence, s.feature_id,
                        s.reference_id, v.filters_id
                 FROM variant_tosnp AS v
                 LEFT JOIN variant_snp AS s
                 ON v.snp_id=s.id
                 LEFT JOIN sample_sample AS a
                 ON v.sample_id=a.id
                 WHERE v.sample_id IN ({0}) AND
                       (a.is_public=TRUE OR a.user_id={1}) AND
                       s.annotation_id={2}
                 ORDER BY v.sample_id ASC, v.snp_id ASC;""".format(
            ','.join([str(i) for i in sample_id]),
            user_id,
            annotation_id
        )
    else:
        sql = """SELECT v.sample_id, v.snp_id, s.annotation_id,
                        s.reference_position, s.reference_base,
                        s.alternate_base,
                        s.reference_codon, s.alternate_codon,
                        s.reference_amino_acid, s.alternate_amino_acid,
                        s.amino_acid_change, s.is_synonymous, s.is_transition,
                        s.is_genic, v.confidence, s.feature_id,
                        s.reference_id, v.filters_id
                 FROM variant_tosnp AS v
                 LEFT JOIN variant_snp AS s
                 ON v.snp_id=s.id
                 LEFT JOIN sample_sample AS a
                 ON v.sample_id=a.id
                 WHERE v.sample_id IN ({0}) AND
                       (a.is_public=TRUE OR a.user_id={1})
                 ORDER BY v.sample_id ASC, v.snp_id ASC;""".format(
            ','.join([str(i) for i in sample_id]),
            user_id
        )

    results = []
    for row in query_database(sql):
        confidence = row['confidence']
        results.append(OrderedDict([
            ('sample_id', row['sample_id']),
            ('snp_id', row['snp_id']),
            ('annotation_id', row['annotation_id']),
            ('reference_position', row['reference_position']),
            ('reference_base', row['reference_base']),
            ('alternate_base', row['alternate_base']),
            ('reference_codon', row['reference_codon']),
            ('alternate_codon', row['alternate_codon']),
            ('reference_amino_acid', row['reference_amino_acid']),
            ('alternate_amino_acid', row['alternate_amino_acid']),
            ('amino_acid_change', row['amino_acid_change']),
            ('is_synonymous', row['is_synonymous']),
            ('is_transition', row['is_transition']),
            ('is_genic', row['is_genic']),
            ('AC', confidence['AC']),
            ('GT', confidence['GT']),
            ('AD', confidence['AD']),
            ('GQ', confidence['GQ']),
            ('AF', confidence['AF']),
            ('MQ', confidence['MQ']),
            ('PL', confidence['PL']),
            ('DP', confidence['DP']),
            ('QD', confidence['QD']),
            ('quality', confidence['quality']),
            ('feature_id', row['feature_id']),
            ('reference_id', row['reference_id']),
            ('filters_id', row['filters_id']),
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
