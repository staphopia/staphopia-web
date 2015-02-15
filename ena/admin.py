from django.contrib import admin

from ena.models import (
    ToSample,
    Study,
    Experiment,
    Run
)


@admin.register(ToSample)
class ToSampleAdmin(admin.ModelAdmin):
    list_display = (
        'experiment_accession', 'sample'
    )


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = (
        'study_accession', 'secondary_study_accession', 'study_title',
        'study_alias'
    )


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        'experiment_accession',
        'experiment_title',
        'experiment_alias',
        'study_accession',
        'sample_accession',
        'secondary_sample_accession',
        'submission_accession',
        'tax_id',
        'scientific_name',
        'instrument_platform',
        'instrument_model',
        'library_layout',
        'library_strategy',
        'library_selection',
        'center_name'
    )


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = (
        'run_accession', 'experiment_accession', 'is_paired', 'run_alias',
        'read_count', 'base_count', 'mean_read_length', 'coverage',
        'first_public', 'fastq_bytes', 'fastq_md5', 'fastq_aspera', 'fastq_ftp'
    )
