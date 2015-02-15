CREATE OR REPLACE VIEW samples_summary AS
SELECT
    -- Sample
    sample.id,
    sample.sample_tag,
    (SELECT username FROM auth_user WHERE id=sample.user_id) AS username,
    sample.contact_name,
    sample.contact_email,
    sample.contact_link,
    sample.sequencing_center,
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
    (SELECT COUNT(variant_id) FROM analysis_varianttosnp WHERE variant_id=variant.id) AS total_snps,
    (SELECT COUNT(variant_id) FROM analysis_varianttoindel WHERE variant_id=variant.id) AS total_indels,

    -- MLST
    (SELECT "ST" FROM analysis_mlstsrst2 WHERE mlst_id=mlst.id) AS st_srst,
    COALESCE((SELECT "ST" FROM analysis_mlstsequencetype WHERE arcc.locus_id=arcc
        AND aroe.locus_id=aroe AND glpf.locus_id=glpf AND gmk.locus_id=gmk
        AND pta.locus_id=pta AND tpi.locus_id=tpi AND yqil.locus_id=yqil
        AND arcc.pident=100 AND aroe.pident=100 AND glpf.pident=100
        AND gmk.pident=100 AND pta.pident=100 AND tpi.pident=100
        AND yqil.pident=100), 0) AS st_blast
FROM analysis_assemblystat as assembly
LEFT JOIN analysis_fastqstat AS fq ON assembly.sample_id=fq.sample_id AND fq.is_original is FALSE
LEFT JOIN samples_sample AS sample ON sample.id=assembly.sample_id
LEFT JOIN analysis_mlst AS mlst ON assembly.sample_id=mlst.sample_id
LEFT JOIN analysis_variant AS variant ON assembly.sample_id=variant.sample_id
LEFT JOIN analysis_mlstblast AS arcc ON mlst.id=arcc.id AND arcc.locus_name='arcc'
LEFT JOIN analysis_mlstblast AS aroe ON mlst.id=aroe.id AND aroe.locus_name='aroe'
LEFT JOIN analysis_mlstblast AS glpf ON mlst.id=glpf.id AND glpf.locus_name='glpf'
LEFT JOIN analysis_mlstblast AS gmk ON mlst.id=gmk.id AND gmk.locus_name='gmk'
LEFT JOIN analysis_mlstblast AS pta ON mlst.id=pta.id AND pta.locus_name='pta'
LEFT JOIN analysis_mlstblast AS tpi ON mlst.id=tpi.id AND tpi.locus_name='tpi'
LEFT JOIN analysis_mlstblast AS yqil ON mlst.id=yqil.id AND yqil.locus_name='yqil'
WHERE assembly.is_scaffolds is FALSE;
