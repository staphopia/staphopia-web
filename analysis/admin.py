from django.contrib import admin

from analysis.models import (
    FastqStat,
    AssemblyStat,
    PipelineVersion,
    Variant,
    VariantAnnotation,
    VariantComment,
    VariantFilter,
    VariantIndel,
    VariantReference,
    VariantSNP,
    VariantToIndel,
    VariantToSNP,
    MLST,
    MLSTSequenceType,
    MLSTBlast,
    MLSTSrst2
)


@admin.register(FastqStat)
class FastqAdmin(admin.ModelAdmin):
    list_display = (
        'sample_tag', 'is_original', 'pipeline_version', 'sequence_rank',
        'total_bp', 'total_reads', 'coverage', 'min_read_length',
        'mean_read_length', 'max_read_length', 'qual_mean', 'qual_std',
        'qual_25th', 'qual_median', 'qual_75th'
    )


@admin.register(AssemblyStat)
class AssemblyAdmin(admin.ModelAdmin):
    list_display = (
        'sample_tag', 'is_scaffolds', 'pipeline_version', 'total_contig',
        'total_contig_length', 'min_contig_length', 'median_contig_length',
        'mean_contig_length', 'max_contig_length', 'n50_contig_length',
        'contigs_greater_1k', 'contigs_greater_10k', 'contigs_greater_100k',
        'contigs_greater_1m'
    )


@admin.register(PipelineVersion)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('module', 'version')


@admin.register(VariantAnnotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = (
        'locus_tag', 'gene', 'protein_id', 'db_xref', 'fixed_product',
        'fixed_note'
    )


@admin.register(VariantToSNP)
class ToSNPAdmin(admin.ModelAdmin):
    list_display = (
        'variant_id',
        'snp_id',
        'comment',
        'filters',
        'AC', 'AD', 'AF', 'DP', 'GQ', 'GT', 'MQ', 'PL', 'QD',
        'quality'
    )


@admin.register(VariantSNP)
class SNPAdmin(admin.ModelAdmin):
    list_display = (
        'locus_tag',
        'reference_position', 'reference_base', 'alternate_base',
        'reference_codon', 'alternate_codon',
        'reference_amino_acid', 'alternate_amino_acid',
        'codon_position', 'snp_codon_position', 'amino_acid_change',
        'is_synonymous', 'is_transition', 'is_genic'
    )


@admin.register(VariantToIndel)
class ToIndelAdmin(admin.ModelAdmin):
    list_display = (
        'variant_id',
        'indel_id',
        'filters',
        'AC', 'AD', 'AF', 'DP', 'GQ', 'GT', 'MQ', 'PL', 'QD',
        'quality'
    )


@admin.register(VariantIndel)
class IndelAdmin(admin.ModelAdmin):
    list_display = (
        'reference_strain', 'locus_tag', 'reference_position',
        'reference_base', 'alternate_base', 'is_deletion'
    )


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('sample_tag', 'pipeline_version')


@admin.register(MLST)
class MLSTAdmin(admin.ModelAdmin):
    list_display = ('sample_tag', 'pipeline_version')


@admin.register(MLSTSequenceType)
class SequenceTypeAdmin(admin.ModelAdmin):
    list_display = ('ST', 'arcc', 'aroe', 'glpf', 'gmk', 'pta', 'tpi', 'yqil',
                    'last_updated')


@admin.register(MLSTBlast)
class MLSTBlastAdmin(admin.ModelAdmin):
    list_display = ('sample_tag', 'locus_name', 'locus_id', 'bitscore', 'slen',
                    'length', 'gaps', 'mismatch', 'pident', 'evalue')


@admin.register(MLSTSrst2)
class Srst2Admin(admin.ModelAdmin):
    list_display = ('sample_tag', 'ST', 'arcc', 'aroe', 'glpf', 'gmk', 'pta',
                    'tpi', 'yqil', 'mismatches', 'uncertainty', 'depth',
                    'maxMAF')


# Single column Tables
admin.site.register(VariantComment)
admin.site.register(VariantFilter)
admin.site.register(VariantReference)
