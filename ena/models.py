"""ENA related models."""
from django.db import models

from sample.models import Publication


class Status(models.Model):
    """Keep track of processed genomes."""

    experiment_accession = models.OneToOneField(
        'Experiment',
        db_column='experiment_accession',
        on_delete=models.CASCADE
    )
    server = models.TextField()
    path = models.TextField()
    status = models.TextField()


class SraLink(models.Model):
    """Store SRA UIDs to prevent redundant Entrez queries."""

    experiment_accession = models.OneToOneField(
        'Experiment',
        db_column='experiment_accession',
        on_delete=models.CASCADE
    )
    uid = models.TextField(unique=True)
    last_checked = models.DateTimeField(auto_now=True)


class Study(models.Model):
    """ENA Studies."""

    study_accession = models.TextField(primary_key=True)
    secondary_study_accession = models.TextField()
    study_title = models.TextField()
    study_alias = models.TextField()


class Experiment(models.Model):
    """ENA experiments."""

    experiment_accession = models.TextField(primary_key=True)
    experiment_title = models.TextField()
    experiment_alias = models.TextField()
    study_accession = models.ForeignKey('Study',
                                        db_column='study_accession',
                                        on_delete=models.CASCADE)
    sample_accession = models.TextField()
    secondary_sample_accession = models.TextField()
    submission_accession = models.TextField()
    tax_id = models.TextField()
    scientific_name = models.TextField()
    instrument_platform = models.TextField(db_index=True, default='')
    instrument_model = models.TextField()
    library_layout = models.TextField()
    library_strategy = models.TextField()
    library_selection = models.TextField()
    center_name = models.TextField()
    coverage = models.DecimalField(db_index=True, max_digits=10,
                                   decimal_places=2, default=0)


class Run(models.Model):
    """ENA runs."""

    run_accession = models.TextField(primary_key=True)
    experiment_accession = models.ForeignKey('Experiment',
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    is_paired = models.BooleanField(default=False)
    run_alias = models.TextField()
    read_count = models.BigIntegerField()
    base_count = models.BigIntegerField()
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=2)
    coverage = models.DecimalField(max_digits=10, decimal_places=2)
    first_public = models.TextField()
    fastq_bytes = models.TextField()
    fastq_md5 = models.TextField()
    fastq_aspera = models.TextField()
    fastq_ftp = models.TextField()


class BioSample(models.Model):
    """ENA Sample Information."""
    accession = models.TextField(unique=True)
    secondary_sample_accession = models.TextField(unique=True)
    bio_material = models.TextField()
    cell_line = models.TextField()
    cell_type = models.TextField()
    collected_by = models.TextField()
    collection_date = models.TextField()
    country = models.TextField()
    cultivar = models.TextField()
    culture_collection = models.TextField()
    description = models.TextField()
    dev_stage = models.TextField()
    ecotype = models.TextField()
    environmental_sample = models.TextField()
    first_public = models.TextField()
    germline = models.TextField()
    identified_by = models.TextField()
    isolate = models.TextField()
    isolation_source = models.TextField()
    location = models.TextField()
    mating_type = models.TextField()
    serotype = models.TextField()
    serovar = models.TextField()
    sex = models.TextField()
    submitted_sex = models.TextField()
    specimen_voucher = models.TextField()
    strain = models.TextField()
    sub_species = models.TextField()
    sub_strain = models.TextField()
    tissue_lib = models.TextField()
    tissue_type = models.TextField()
    variety = models.TextField()
    tax_id = models.TextField()
    scientific_name = models.TextField()
    sample_alias = models.TextField()
    checklist = models.TextField()
    center_name = models.TextField()
    depth = models.TextField()
    elevation = models.TextField()
    altitude = models.TextField()
    environment_biome = models.TextField()
    environment_feature = models.TextField()
    environment_material = models.TextField()
    temperature = models.TextField()
    salinity = models.TextField()
    sampling_campaign = models.TextField()
    sampling_site = models.TextField()
    sampling_platform = models.TextField()
    protocol_label = models.TextField()
    project_name = models.TextField()
    host = models.TextField()
    host_tax_id = models.TextField()
    host_status = models.TextField()
    host_sex = models.TextField()
    submitted_host_sex = models.TextField()
    host_body_site = models.TextField()
    host_gravidity = models.TextField()
    host_phenotype = models.TextField()
    host_genotype = models.TextField()
    host_growth_conditions = models.TextField()
    environmental_package = models.TextField()
    investigation_type = models.TextField()
    experimental_factor = models.TextField()
    sample_collection = models.TextField()
    sequencing_method = models.TextField()
    target_gene = models.TextField()
    ph = models.TextField()
    broker_name = models.TextField()


class CenterNames(models.Model):
    """Convert ENA abbreviations to readable names."""

    ena_name = models.TextField(unique=True)
    name = models.TextField()
    link = models.TextField()


class ToPublication(models.Model):
    """Links ENA entries to a publication."""

    experiment_accession = models.ForeignKey('Experiment',
                                             db_column='experiment_accession',
                                             on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE,
                                    related_name="publication",)


class GoogleScholar(models.Model):
    """Store google scholar information."""

    accession = models.TextField(db_index=True)
    title = models.TextField()
    url = models.TextField()
    cluster_id = models.TextField()
    url_citations = models.TextField()
