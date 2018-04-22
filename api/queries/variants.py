"""API utilities for variant related viewsets."""
from collections import OrderedDict

from api.utils import query_database
from api.queries.samples import get_samples

from staphopia.utils import reverse_complement

from variant.models import ReferenceGenome

def get_variant_count_by_position(ids, is_annotation=False):
    sql = """SELECT id, position, reference_id, annotation_id,
                    is_mlst_set, nongenic_indel, nongenic_snp, indel,
                    synonymous, nonsynonymous, total
             FROM variant_counts
             WHERE {0} IN ({1})
             ORDER BY position;""".format(
        'annotation_id' if is_annotation else 'position',
        ','.join([str(i) for i in ids])
    )

    return query_database(sql)


def get_variant_counts(sample_id, user_id):
    sql = """SELECT v.sample_id, snp_count, indel_count,
                    (snp_count + indel_count) AS total
             FROM variant_variant AS v
             LEFT JOIN sample_sample AS s
             ON v.sample_id=s.id
             WHERE v.sample_id IN ({0}) USER_PERMISSION;""".format(
        ','.join([str(i) for i in sample_id])
    )

    return query_database(sql)


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
                 WHERE v.sample_id IN ({0}) USER_PERMISSION;""".format(
            ','.join([str(i) for i in sample_id])
        )
    else:
        sql = """SELECT v.sample_id, v.indel
                 FROM variant_variant AS v
                 LEFT JOIN sample_sample AS s
                 ON v.sample_id=s.id
                 WHERE v.sample_id IN ({0}) USER_PERMISSION;""".format(
            ','.join([str(i) for i in sample_id])
        )

    rows = {}
    indel_id = []
    for row in query_database(sql):
        rows[row['sample_id']] = row['indel']
        indels = []
        for indel in row['indel']:
            indels.append(indel['indel_id'])
        indel_id = list(set(indel_id + list(indels)))

    results = []
    if indel_id:
        indel_info = {}
        if annotation_id:
            if isinstance(annotation_id, str):
                annotation_id = [annotation_id]
            sql = """SELECT *
                     FROM variant_indel
                     WHERE id IN ({0}) AND annotation_id IN ({1})""".format(
                ','.join([str(i) for i in indel_id]),
                ','.join([str(i) for i in annotation_id])
            )
        else:
            sql = "SELECT * FROM variant_indel WHERE id IN ({0})".format(
                ','.join([str(i) for i in indel_id])
            )
        for row in query_database(sql):
            indel_info[row['id']] = row

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


def get_snps_by_sample(sample_id, user_id, annotation_id=None, start=None,
                       end=None):
    """Return snps associated with a sample."""
    sql = """SELECT v.sample_id, v.snp
             FROM variant_variant AS v
             LEFT JOIN sample_sample AS s
             ON v.sample_id=s.id
             WHERE v.sample_id IN ({0}) USER_PERMISSION;""".format(
        ','.join([str(i) for i in sample_id])
    )

    rows = {}
    snp_id = []
    for row in query_database(sql):
        rows[row['sample_id']] = row['snp']
        snps = []
        for snp in row['snp']:
            snps.append(snp['snp_id'])
        snp_id = list(set(snp_id + list(snps)))

    results = []
    if snp_id:
        snp_info = {}
        if annotation_id:
            if isinstance(annotation_id, str):
                annotation_id = [annotation_id]

            sql = """SELECT *
                     FROM variant_snp
                     WHERE id IN ({0}) AND annotation_id IN ({1})""".format(
                ','.join([str(i) for i in snp_id]),
                ','.join([str(i) for i in annotation_id])
            )
        elif start and end:
            sql = """SELECT *
                     FROM variant_snp
                     WHERE reference_position >= {0} AND
                           reference_position <= {1};""".format(
                start, end
            )
        else:
            sql = "SELECT * FROM variant_snp WHERE id IN ({0})".format(
                ','.join([str(i) for i in snp_id])
            )

        for row in query_database(sql):
            snp_info[row['id']] = row

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


def clean_annotation(string):
    return string.replace(
        '[semi-colon]', ';'
    ).replace(
        '[comma]', ','
    ).replace(
        '[space]', ' '
    )


def get_variant_annotation(annotation_ids, locus_tag=None):
    """Get variant annotation information for a set of annotation ids."""
    locus_sql = ""
    if locus_tag:
        locus_sql = f"AND locus_tag='{locus_tag}'"

    sql = None
    if annotation_ids:
        sql = """SELECT * FROM variant_annotation
                 WHERE id IN ({0}) {1}
                 ORDER BY id;""".format(
            ','.join([str(i) for i in annotation_ids]),
            locus_sql
        )
    else:
        if locus_tag:
            sql = """SELECT * FROM variant_annotation
                     WHERE locus_tag='{0}'
                     ORDER BY id;""".format(locus_tag)
        else:
            sql = "SELECT * FROM variant_annotation ORDER BY id;"

    results = []
    for row in query_database(sql):
        row['note'] = clean_annotation(row['note'])
        row['gene'] = clean_annotation(row['gene'])
        row['locus_tag'] = clean_annotation(row['locus_tag'])
        row['product'] = clean_annotation(row['product'])
        row['protein_id'] = clean_annotation(row['protein_id'])
        results.append(row)

    return results


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


def get_annotation_strand(annotation_ids):
    """Get the strand info for a set of annotation ids."""
    sql = """SELECT id, reference_id, strand FROM variant_annotation
             WHERE id IN ({0});""".format(
        ','.join([str(i) for i in annotation_ids])
    )

    return query_database(sql)


def get_representative_sequence(sample_ids, user_id, annotation_ids):
    """Return fasta formatted sequence."""
    # Get annotation info
    strand = {}
    reference = None
    for row in get_annotation_strand(annotation_ids):
        if not reference:
            reference = ReferenceGenome.objects.get(
                reference_id=row['reference_id']
            ).sequence
        strand[row['id']] = row['strand']

    annotations = {}
    indels = {'reference': {}}
    for annotation_id in annotation_ids:
        annotations[annotation_id] = OrderedDict()
        indels['reference'][annotation_id] = False
        for sample_id in sample_ids:
            if sample_id not in indels:
                indels[sample_id] = {}
            indels[sample_id][annotation_id] = False

    sequences = OrderedDict()
    sequences['reference'] = OrderedDict()
    for position, vals in reference.items():
        if vals['annotation_id'] in annotations:
            if vals['annotation_id'] not in sequences['reference']:
                sequences['reference'][vals['annotation_id']] = []
            annotations[vals['annotation_id']][position] = vals['base'].lower()
            sequences['reference'][vals['annotation_id']].append(
                vals['base'].lower()
            )
    # Get snp_ids with annotation id
    snps = {}
    for snp in get_snps_by_sample(sample_ids, user_id,
                                  annotation_id=annotation_ids):
        sample_id = snp['sample_id']
        if snp['sample_id'] not in snps:
            snps[sample_id] = {}

        position = str(snp['reference_position'])
        if snp['reference_position'] not in snps[sample_id]:
            snps[sample_id][position] = snp['alternate_base']

    for indel in get_indels_by_sample(sample_ids, user_id,
                                      annotation_id=annotation_ids):
        indels[indel['sample_id']][indel["annotation_id"]] = True

    """
    {"ids":[5000,5001,5002],"extra":{"annotation_ids":[6]}}
    """
    # Substitute sequence
    for sample_id in sample_ids:
        sequences[sample_id] = OrderedDict()
        for annotation_id, vals in annotations.items():
            sequences[sample_id][annotation_id] = []
            for position, base in vals.items():
                if sample_id in snps:
                    if position in snps[sample_id]:
                        sequences[sample_id][annotation_id].append(
                            snps[sample_id][position]
                        )
                    else:
                        sequences[sample_id][annotation_id].append(base)
                else:
                    sequences[sample_id][annotation_id].append(base)

    # Generate Sequences
    concatenated = []
    for sample, annotation in sequences.items():
        for annotation_id, seq in annotation.items():
            sequence = None
            if strand[annotation_id]:
                sequence = ''.join(seq)
            else:
                sequence = ''.join(reverse_complement(seq))

            concatenated.append(OrderedDict([
                ('sample_id', sample),
                ('annotation_id', annotation_id),
                ('total_snps', sum(1 for s in sequence if s.isupper())),
                ('has_indel', indels[sample][annotation_id]),
                ('sequence', sequence)
            ]))

    return concatenated
