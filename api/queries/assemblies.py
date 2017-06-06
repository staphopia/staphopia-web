"""API utilities for Assembly related viewsets."""
from api.utils import query_database


def get_assembly_stats(sample_ids, is_scaffolds='FALSE', is_plasmids='FALSE'):
    """Return assembly stats for a set of sample ids."""
    cols = [
        'sample_id', 'is_scaffolds', 'is_plasmids', 'total_contig',
        'total_contig_length', 'min_contig_length', 'median_contig_length',
        'mean_contig_length', 'max_contig_length', 'n50_contig_length',
        'l50_contig_count', 'ng50_contig_length', 'lg50_contig_count',
        'contigs_greater_1k', 'contigs_greater_10k', 'contigs_greater_100k',
        'contigs_greater_1m', 'percent_contigs_greater_1k',
        'percent_contigs_greater_10k', 'percent_contigs_greater_100k',
        'percent_contigs_greater_1m', 'contig_percent_a', 'contig_percent_t',
        'contig_percent_g', 'contig_percent_c', 'contig_percent_n',
        'contig_non_acgtn', 'num_contig_non_acgtn'
    ]

    sql = """SELECT {0}
             FROM assembly_stats
             WHERE sample_id IN ({1}) AND is_scaffolds={2} AND is_plasmids={3}
             ORDER BY sample_id;""".format(
        ','.join(cols),
        ','.join([str(i) for i in sample_ids]),
        is_scaffolds,
        is_plasmids
    )

    return query_database(sql)
