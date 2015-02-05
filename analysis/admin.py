from django.contrib import admin

from analysis.models import FastqStat, AssemblyStat, PipelineVersion


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
