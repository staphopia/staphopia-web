COLUMNS = {
    'gene_features': [
        'g.id', 'g.start', 'g.end', 'g.is_positive', 'g."is_tRNA"',
        'g."is_rRNA"', 'g.phase', 'g.prokka_id', 'g.dna', 'g.aa',
        'g.cluster_id', 'c.name AS cluster_name', 'g.contig_id',
        'g.inference_id', 'g.note_id', 'g.product_id', 'p.product',
        'g.sample_id', 'a.annotation_id'
    ]
}
