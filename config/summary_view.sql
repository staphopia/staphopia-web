CREATE OR REPLACE VIEW sample_summary_view AS
SELECT
    -- Sample
    sample.id,
    sample.sample_tag,
    (SELECT username FROM auth_user WHERE id=sample.user_id) AS username,
    sample.contact_name,
    sample.contact_email,
    sample.contact_link,
    (SELECT name from ena_centernames where ena_name=sample.sequencing_center) AS sequencing_center,
    sample.sequencing_center_link,
    sample.sequencing_date,
    sample.sequencing_libaray_method,
    sample.sequencing_platform,
    sample.publication_link,
    sample.pubmed_id,
    sample.doi,
    sample.funding_agency,
    sample.funding_agency_link,
    sample.strain,
    sample.isolation_date,
    sample.isolation_country,
    sample.isolation_city,
    sample.isolation_region,
    sample.host_name,
    sample.host_health,
    sample.host_age,
    sample.host_gender,
    sample.comments,
    sample.vancomycin_mic,
    sample.penicillin_mic,
    sample.oxacillin_mic,
    sample.clindamycin_mic,
    sample.daptomycin_mic,
    sample.levofloxacin_mic,
    sample.linezolid_mic,
    sample.rifampin_mic,
    sample.tetracycline_mic,
    sample.trimethoprim_mic,
    sample.source,
    sample.is_public,
    sample.is_paired,
    sample.is_published,

    -- FASTQ
    CASE fq.rank WHEN 3 THEN 'Gold' WHEN 2 THEN 'Silver' ELSE 'Bronze' END as rank,
    fq.total_bp,
    fq.total_reads,
    fq.coverage,
    fq.min_read_length,
    fq.mean_read_length,
    fq.max_read_length,
    CASE WHEN fq.qual_mean > 41 THEN (fq.qual_mean - 31) ELSE fq.qual_mean END as q_score,
    fq.qual_mean,
    fq.qual_std,
    fq.qual_25th,
    fq.qual_median,
    fq.qual_75th,

    -- Assembly
    assembly.total_contig,
    assembly.total_contig_length,
    assembly.min_contig_length,
    assembly.median_contig_length,
    assembly.mean_contig_length,
    assembly.max_contig_length,
    assembly.n50_contig_length,
    assembly.l50_contig_count,
    assembly.ng50_contig_length,
    assembly.lg50_contig_count,
    assembly.contigs_greater_1k,
    assembly.contigs_greater_10k,
    assembly.contigs_greater_100k,
    assembly.contigs_greater_1m,
    assembly.percent_contigs_greater_1k,
    assembly.percent_contigs_greater_10k,
    assembly.percent_contigs_greater_100k,
    assembly.percent_contigs_greater_1m,
    assembly.contig_percent_a,
    assembly.contig_percent_t,
    assembly.contig_percent_g,
    assembly.contig_percent_c,
    assembly.contig_percent_n,
    assembly.contig_non_acgtn,
    assembly.num_contig_non_acgtn,
    (assembly.contig_percent_g + assembly.contig_percent_c) AS gc_content,

    -- Variants
    variant.snp AS total_snps,
    variant.indel AS total_indels,

    -- MLST
    mlst.st_stripped,
    mlst.st_original,
    mlst.is_exact

FROM assembly_stats as assembly
LEFT JOIN sequence_quality AS fq ON assembly.sample_id=fq.sample_id AND fq.is_original is FALSE
LEFT JOIN sample_metadata AS sample ON sample.id=assembly.sample_id
LEFT JOIN mlst_srst2 AS mlst ON assembly.sample_id=mlst.sample_id
LEFT JOIN variant_counts as variant ON assembly.sample_id=variant.sample_id
WHERE assembly.is_scaffolds is FALSE;

CREATE TABLE sample_summary
AS SELECT * FROM sample_summary_view;
