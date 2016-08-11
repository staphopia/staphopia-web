"""Models associated with Sample."""
from django.db import models
from django.contrib.auth.models import User


class Sample(models.Model):
    """Basic sample information."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sample_tag = models.TextField(db_index=True, default='')
    is_paired = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)
    md5sum = models.CharField(default='', max_length=32, unique=True)


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


class ToMetaData(models.Model):
    """Link samples to metadata."""

    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    metadata = models.ForeignKey('MetaData', on_delete=models.CASCADE)
    value = models.TextField()


class MetaData(models.Model):
    """Meta data associated with a sample."""

    field = models.TextField(unique=True)
    description = models.TextField()


def content_file_name(instance, filename):
    """Determine the content type of an upload."""
    new_name = '{0}_{1}_original.{2}'.format(
        instance.sample.user.username,
        str(instance.sample.sample_id).zfill(6),
        filename.split('.', 1)[1]
    )
    return '/'.join(['uploads', instance.sample.user.username,
                     str(instance.sample.sample_id).zfill(6), new_name])


class Upload(models.Model):
    """Path to uploaded sample."""

    sample = models.OneToOneField('Sample', primary_key=True,
                                  on_delete=models.CASCADE)
    path = models.FileField(default='', upload_to=content_file_name)
    md5sum = models.CharField(default='', max_length=32, unique=True)


class SampleSummary(models.Model):
    """Unmananged model of a database view."""

    id = models.IntegerField(primary_key=True)
    sample_tag = models.TextField(blank=True)
    username = models.CharField(max_length=30, blank=True)
    contact_name = models.TextField(blank=True)
    contact_email = models.CharField(max_length=75, blank=True)
    contact_link = models.CharField(max_length=200, blank=True)
    sequencing_center = models.TextField(blank=True)
    sequencing_center_link = models.CharField(max_length=200, blank=True)
    sequencing_date = models.DateField(blank=True, null=True)
    sequencing_libaray_method = models.TextField(blank=True)
    sequencing_platform = models.TextField(blank=True)
    publication_link = models.CharField(max_length=200, blank=True)
    pubmed_id = models.TextField(blank=True)
    doi = models.TextField(blank=True)
    funding_agency = models.TextField(blank=True)
    funding_agency_link = models.CharField(max_length=200, blank=True)
    strain = models.TextField(blank=True)
    isolation_date = models.DateField(blank=True, null=True)
    isolation_country = models.TextField(blank=True)
    isolation_city = models.TextField(blank=True)
    isolation_region = models.TextField(blank=True)
    host_name = models.TextField(blank=True)
    host_health = models.TextField(blank=True)
    host_age = models.SmallIntegerField(blank=True, null=True)
    host_gender = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    vancomycin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                         blank=True, null=True)
    penicillin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                         blank=True, null=True)
    oxacillin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                        blank=True, null=True)
    clindamycin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                          blank=True, null=True)
    daptomycin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                         blank=True, null=True)
    levofloxacin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                           blank=True, null=True)
    linezolid_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                        blank=True, null=True)
    rifampin_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                       blank=True, null=True)
    tetracycline_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                           blank=True, null=True)
    trimethoprim_mic = models.DecimalField(max_digits=6, decimal_places=3,
                                           blank=True, null=True)
    source = models.TextField(blank=True)
    is_public = models.NullBooleanField()
    is_paired = models.NullBooleanField()
    is_published = models.NullBooleanField()
    rank = models.SmallIntegerField(blank=True, null=True)
    total_bp = models.BigIntegerField(blank=True, null=True)
    total_reads = models.BigIntegerField(blank=True, null=True)
    coverage = models.DecimalField(max_digits=7, decimal_places=2,
                                   blank=True, null=True)
    min_read_length = models.IntegerField(blank=True, null=True)
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=3,
                                           blank=True, null=True)
    max_read_length = models.IntegerField(blank=True, null=True)
    q_score = models.DecimalField(max_digits=6, decimal_places=3,
                                  blank=True, null=True)
    qual_mean = models.DecimalField(max_digits=6, decimal_places=3,
                                    blank=True, null=True)
    qual_std = models.DecimalField(max_digits=6, decimal_places=3,
                                   blank=True, null=True)
    qual_25th = models.DecimalField(max_digits=6, decimal_places=3,
                                    blank=True, null=True)
    qual_median = models.DecimalField(max_digits=6, decimal_places=3,
                                      blank=True, null=True)
    qual_75th = models.DecimalField(max_digits=6, decimal_places=3,
                                    blank=True, null=True)
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
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    percent_contigs_greater_10k = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    percent_contigs_greater_100k = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    percent_contigs_greater_1m = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True
    )
    contig_percent_a = models.DecimalField(max_digits=4, decimal_places=2,
                                           blank=True, null=True)
    contig_percent_t = models.DecimalField(max_digits=4, decimal_places=2,
                                           blank=True, null=True)
    contig_percent_g = models.DecimalField(max_digits=4, decimal_places=2,
                                           blank=True, null=True)
    contig_percent_c = models.DecimalField(max_digits=4, decimal_places=2,
                                           blank=True, null=True)
    contig_percent_n = models.DecimalField(max_digits=4, decimal_places=2,
                                           blank=True, null=True)
    contig_non_acgtn = models.DecimalField(max_digits=4, decimal_places=2,
                                           blank=True, null=True)
    num_contig_non_acgtn = models.SmallIntegerField(blank=True, null=True)
    gc_content = models.DecimalField(max_digits=65535, decimal_places=65535,
                                     blank=True, null=True)
    total_snps = models.PositiveIntegerField(blank=True, null=True)
    total_indels = models.PositiveIntegerField(blank=True, null=True)
    st_stripped = models.PositiveIntegerField(blank=True)
    st_original = models.TextField(blank=True, null=True)
    is_exact = models.BooleanField(blank=True)

    class Meta:
        managed = False
        db_table = 'sample_summary'


class Pipeline(models.Model):
    """Store pipeline version for history purposes."""

    sample = models.OneToOneField('MetaData', unique=True,
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
