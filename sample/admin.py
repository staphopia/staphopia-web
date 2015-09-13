from django.contrib import admin

from sample.models import MetaData, SampleSummary


@admin.register(MetaData)
class SampleAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'sample_tag',

        # Sequence Information
        'is_public',
        'is_paired',
        'is_published',

        # Project Information
        'contact_name',
        'contact_email',
        'contact_link',
        'sequencing_center',
        'sequencing_center_link',
        'sequencing_date',
        'sequencing_libaray_method',
        'sequencing_platform',

        # Publication Inforamtion
        'publication_link',
        'pubmed_id',
        'doi',
        'funding_agency',
        'funding_agency_link',

        # Organism Information
        'strain',
        'isolation_date',
        'isolation_country',
        'isolation_city',
        'isolation_region',
        'host_name',
        'host_health',
        'host_age',
        'host_gender',
        'comments',

        # Phenotype Information
        'vancomycin_mic',
        'penicillin_mic',
        'oxacillin_mic',
        'clindamycin_mic',
        'daptomycin_mic',
        'levofloxacin_mic',
        'linezolid_mic',
        'rifampin_mic',
        'tetracycline_mic',
        'trimethoprim_mic',
        'source'
    )


@admin.register(SampleSummary)
class SamplesSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'sample_tag',

        # Sequence Information
        'is_public',
        'is_paired',
        'is_published',
    )
