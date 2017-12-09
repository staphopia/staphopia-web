"""Models associated with Sample."""
from django.db import models
from django.contrib.auth.models import User


class Sample(models.Model):
    """Basic sample information."""

    user = models.ForeignKey(User, models.CASCADE)
    sample_tag = models.TextField(db_index=True, default='')
    is_paired = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)
    md5sum = models.CharField(default='', max_length=32) # add unique=True once MD5s fixed


class ToResistance(models.Model):
    """Antibiotic resistance tests conducted on a Sample."""

    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    resistance = models.ForeignKey('Resistance', on_delete=models.CASCADE)
    value = models.TextField()
    phenotype = models.TextField()
    specification = models.ForeignKey('ResistanceSpecification',
                                      on_delete=models.CASCADE)


class Resistance(models.Model):
    """Antibiotic resitance tests."""

    antibiotic = models.TextField()
    test = models.TextField()
    unit = models.TextField()

    class Meta:
        unique_together = ('antibiotic', 'test', 'unit')


class ResistanceSpecification(models.Model):
    """Basis for determining the phenotype of a test."""

    susceptible = models.TextField()
    intermediate = models.TextField()
    resistant = models.TextField()
    comment = models.TextField()

    class Meta:
        unique_together = ('susceptible', 'intermediate', 'resistant',
                           'comment')


class Tag(models.Model):
    """User based tags to associate with a sample."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.TextField(db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'tag')


class ToTag(models.Model):
    """Link samples to tags."""

    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)


class ToPublication(models.Model):
    """Link samples and publications."""

    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    publication = models.ForeignKey('Publication', on_delete=models.CASCADE)


class Publication(models.Model):
    """Pubmed information."""

    pmid = models.TextField(unique=True)
    authors = models.TextField()
    title = models.TextField()
    abstract = models.TextField(db_index=True)
    reference_ids = models.TextField()
    keywords = models.TextField()


class SearchHistory(models.Model):
    """Capture search queries (anonymously) to aid in refining searches."""
    query = models.TextField()
    count = models.PositiveIntegerField()


class MetaDataHistory(models.Model):
    """Capture user changes to metadata fields."""
    sample = models.OneToOneField('Sample', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    field = models.TextField()
    previous = models.TextField()
    current = models.TextField()


class MetaData(models.Model):
    """Meta data associated with a sample."""

    sample = models.OneToOneField('Sample', on_delete=models.CASCADE)
    contains_ena_metadata = models.BooleanField(default=True)
    study_accession = models.TextField(default="",)
    study_title = models.TextField(
        default="",
        help_text="Title of the study as would be used in a publication."
    )
    study_alias = models.TextField(default="",)

    secondary_study_accession = models.TextField(default="",)
    sample_accession = models.TextField(default="",)
    secondary_sample_accession = models.TextField(default="",)
    submission_accession = models.TextField(default="",)
    experiment_accession = models.TextField(default="",)
    experiment_title = models.TextField(
        default="",
        help_text=("Short text that can be used to call out experiment "
                   "records in searches or in displays.")
    )
    experiment_alias = models.TextField(default="",)

    tax_id = models.PositiveIntegerField(
        default="",
        help_text="NCBI Taxonomy Identifier."
    )
    scientific_name = models.TextField(
        default="",
        help_text="Scientific name of sample that distinguishes its taxonomy."
    )

    instrument_platform = models.TextField(
        default="",
        help_text=("Which sequencing platform and platform-specific "
                   "runtime parameters.")
    )
    instrument_model = models.TextField(
        default="",
        help_text="Specific model of the platform used for sequencing."
    )
    library_layout = models.TextField(
        default="",
        help_text="Single, paired or other configuration of reads."
    )
    library_strategy = models.TextField(
        default="",
        help_text="Sequencing technique intended for this library."
    )
    library_selection = models.TextField(default="", help_text="")

    center_name = models.TextField(
        default="",
        help_text="Sequencing center that submitted the sample to ENA/SRA"
    )
    center_link = models.TextField(
        default="",
        help_text="Sequencing center link that submitted the sample to ENA/SRA"
    )
    first_public = models.DateField(
        default="",
        help_text="Date sample was submitted to ENA/SRA."
    )

    # BioSample fields
    cell_line = models.TextField(default="")
    collected_by = models.TextField(default="")
    collection_date = models.TextField(default="")
    location = models.TextField(default="")
    country = models.TextField(default="")
    region = models.TextField(default="")
    description = models.TextField(default="")
    environmental_sample = models.TextField(default="")
    biosample_first_public = models.TextField(default="")
    germline = models.TextField(default="")
    isolate = models.TextField(default="")
    isolation_source = models.TextField(default="")
    coordinates = models.TextField(default="")
    serotype = models.TextField(default="")
    serovar = models.TextField(default="")
    sex = models.TextField(default="")
    submitted_sex = models.TextField(default="")
    strain = models.TextField(default="")
    sub_species = models.TextField(default="")
    tissue_type = models.TextField(default="")
    biosample_tax_id = models.TextField(default="")
    biosample_scientific_name = models.TextField(default="")
    sample_alias = models.TextField(default="")
    checklist = models.TextField(default="")
    biosample_center_name = models.TextField(default="")
    environment_biome = models.TextField(default="")
    environment_feature = models.TextField(default="")
    environment_material = models.TextField(default="")
    project_name = models.TextField(default="")
    host = models.TextField(default="")
    host_tax_id = models.TextField(default="")
    host_status = models.TextField(default="")
    host_sex = models.TextField(default="")
    submitted_host_sex = models.TextField(default="")
    host_body_site = models.TextField(default="")
    investigation_type = models.TextField(default="")
    sequencing_method = models.TextField(default="")
    broker_name = models.TextField(default="")


class SampleSummary(models.Model):
    id = models.IntegerField(primary_key=True)
    sample_id = models.IntegerField(blank=True, null=True)
    is_paired = models.NullBooleanField()
    is_public = models.NullBooleanField()
    is_published = models.NullBooleanField()
    sample_tag = models.TextField(blank=True, null=True)
    document = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    contains_ena_metadata = models.NullBooleanField()
    study_accession = models.TextField(blank=True, null=True)
    study_title = models.TextField(blank=True, null=True)
    study_alias = models.TextField(blank=True, null=True)
    secondary_study_accession = models.TextField(blank=True, null=True)
    sample_accession = models.TextField(blank=True, null=True)
    secondary_sample_accession = models.TextField(blank=True, null=True)
    submission_accession = models.TextField(blank=True, null=True)
    experiment_accession = models.TextField(blank=True, null=True)
    experiment_title = models.TextField(blank=True, null=True)
    experiment_alias = models.TextField(blank=True, null=True)
    tax_id = models.IntegerField(blank=True, null=True)
    scientific_name = models.TextField(blank=True, null=True)
    instrument_platform = models.TextField(blank=True, null=True)
    instrument_model = models.TextField(blank=True, null=True)
    library_layout = models.TextField(blank=True, null=True)
    library_strategy = models.TextField(blank=True, null=True)
    library_selection = models.TextField(blank=True, null=True)
    center_name = models.TextField(blank=True, null=True)
    center_link = models.TextField(blank=True, null=True)
    cell_line = models.TextField(blank=True, null=True)
    collected_by = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    coordinates = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    environmental_sample = models.TextField(blank=True, null=True)
    biosample_first_public = models.TextField(blank=True, null=True)
    germline = models.TextField(blank=True, null=True)
    isolate = models.TextField(blank=True, null=True)
    isolation_source = models.TextField(blank=True, null=True)
    serotype = models.TextField(blank=True, null=True)
    serovar = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    submitted_sex = models.TextField(blank=True, null=True)
    strain = models.TextField(blank=True, null=True)
    sub_species = models.TextField(blank=True, null=True)
    tissue_type = models.TextField(blank=True, null=True)
    biosample_scientific_name = models.TextField(blank=True, null=True)
    sample_alias = models.TextField(blank=True, null=True)
    checklist = models.TextField(blank=True, null=True)
    biosample_center_name = models.TextField(blank=True, null=True)
    environment_biome = models.TextField(blank=True, null=True)
    environment_feature = models.TextField(blank=True, null=True)
    environment_material = models.TextField(blank=True, null=True)
    project_name = models.TextField(blank=True, null=True)
    host = models.TextField(blank=True, null=True)
    host_status = models.TextField(blank=True, null=True)
    host_sex = models.TextField(blank=True, null=True)
    submitted_host_sex = models.TextField(blank=True, null=True)
    host_body_site = models.TextField(blank=True, null=True)
    investigation_type = models.TextField(blank=True, null=True)
    sequencing_method = models.TextField(blank=True, null=True)
    broker_name = models.TextField(blank=True, null=True)
    rank = models.TextField(blank=True, null=True)
    total_bp = models.BigIntegerField(blank=True, null=True)
    read_total = models.BigIntegerField(blank=True, null=True)
    coverage = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True
    )
    read_min = models.IntegerField(blank=True, null=True)
    read_mean = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    read_median = models.IntegerField(blank=True, null=True)
    read_std = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    read_max = models.IntegerField(blank=True, null=True)
    read_25th = models.IntegerField(blank=True, null=True)
    read_75th = models.IntegerField(blank=True, null=True)
    q_score = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    qual_mean = models.DecimalField(
        max_digits=7, decimal_places=4, blank=True, null=True
    )
    qual_std = models.DecimalField(
        max_digits=7, decimal_places=4, blank=True, null=True
    )
    qual_25th = models.IntegerField(blank=True, null=True)
    qual_median = models.IntegerField(blank=True, null=True)
    qual_75th = models.IntegerField(blank=True, null=True)
    total_contig = models.SmallIntegerField(blank=True, null=True)
    total_contig_length = models.IntegerField(blank=True, null=True)
    min_contig_length = models.IntegerField(blank=True, null=True)
    median_contig_length = models.IntegerField(blank=True, null=True)
    mean_contig_length = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    max_contig_length = models.IntegerField(blank=True, null=True)
    n50_contig_length = models.IntegerField(blank=True, null=True)
    l50_contig_count = models.SmallIntegerField(blank=True, null=True)
    ng50_contig_length = models.IntegerField(blank=True, null=True)
    lg50_contig_count = models.SmallIntegerField(blank=True, null=True)
    contigs_greater_1k = models.SmallIntegerField(blank=True, null=True)
    contigs_greater_10k = models.SmallIntegerField(blank=True, null=True)
    contigs_greater_100k = models.SmallIntegerField(blank=True, null=True)
    contigs_greater_1m = models.SmallIntegerField(blank=True, null=True)
    percent_contigs_greater_1k = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    percent_contigs_greater_10k = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    percent_contigs_greater_100k = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    percent_contigs_greater_1m = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    contig_percent_a = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    contig_percent_t = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    contig_percent_g = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    contig_percent_c = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    contig_percent_n = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    contig_non_acgtn = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    num_contig_non_acgtn = models.SmallIntegerField(blank=True, null=True)
    gc_content = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    total_snps = models.IntegerField(blank=True, null=True)
    total_indels = models.IntegerField(blank=True, null=True)
    st_original = models.TextField(blank=True, null=True)
    st_stripped = models.TextField(blank=True, null=True)
    is_exact = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'sample_summary'


class Pipeline(models.Model):
    """Store pipeline version for history purposes."""
    sample = models.OneToOneField('Sample', unique=True,
                                  on_delete=models.CASCADE)
    assembly = models.TextField()
    gene = models.TextField()
    kmer = models.TextField()
    mlst = models.TextField()
    sequence = models.TextField()
    variant = models.TextField()


class Program(models.Model):
    """Store information about a program."""

    program = models.TextField()
    version = models.TextField()
    comments = models.TextField()


def content_file_name(instance, filename):
    """Determine the content type of an upload."""
    new_name = '{0}_{1}_original.{2}'.format(
        instance.sample.user.username,
        str(instance.sample.sample_id).zfill(6),
        filename.split('.', 1)[1]
    )
    return '/'.join(['uploads', instance.sample.user.username,
                     str(instance.sample.sample_id).zfill(6), new_name])
