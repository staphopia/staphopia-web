""" Table models for analysis results. """
from django.db import models

from samples.models import Sample


class PipelineVersion(models.Model):

    """ Store pipeline version for history purposes. """

    module = models.TextField()
    version = models.TextField()

    class Meta:
        unique_together = ('module', 'version')


class Program(models.Model):

    """ Store versions to specific programs used throughout the pipeline. """

    pipeline = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)
    program = models.TextField()
    version = models.TextField()

    class Meta:
        unique_together = ('pipeline', 'program', 'version')


class FastqStat(models.Model):

    """
    Statistics of input FASTQ file.

    Can store original and filtered stats.
    """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False, db_index=True)
    version = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)

    rank = models.PositiveSmallIntegerField(db_index=True)

    total_bp = models.BigIntegerField()
    total_reads = models.BigIntegerField()
    coverage = models.DecimalField(max_digits=7, decimal_places=2)

    min_read_length = models.PositiveIntegerField()
    mean_read_length = models.DecimalField(max_digits=10, decimal_places=3)
    max_read_length = models.PositiveIntegerField()

    qual_mean = models.DecimalField(max_digits=6, decimal_places=3)
    qual_std = models.DecimalField(max_digits=6, decimal_places=3)
    qual_25th = models.DecimalField(max_digits=6, decimal_places=3)
    qual_median = models.DecimalField(max_digits=6, decimal_places=3)
    qual_75th = models.DecimalField(max_digits=6, decimal_places=3)

    class Meta:
        unique_together = ('sample', 'is_original', 'version')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    def sequence_rank(self):
        """ Display medal rank in admin view. """
        ranks = {1: 'Bronze', 2: 'Silver', 3: 'Gold'}
        return ranks[self.rank]
    sequence_rank.short_description = 'Rank'
    sequence_rank.admin_order_field = 'rank'

    def pipeline_version(self):
        """ Display pipeline version in admin view. """
        return self.version.version
    pipeline_version.short_description = 'Pipeline Version'
    pipeline_version.admin_order_field = 'version'


class AssemblyStat(models.Model):

    """
    Statistics of the assembled genome.

    Both contigs and scaffolds are stored. At the moment because pipeline
    ignores paired end reads, the scaffolds may not be meaningful.
    """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    is_scaffolds = models.BooleanField(default=False, db_index=True)
    version = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)

    total_contig = models.PositiveSmallIntegerField()
    total_contig_length = models.PositiveIntegerField()

    min_contig_length = models.PositiveIntegerField()
    median_contig_length = models.PositiveIntegerField()
    mean_contig_length = models.DecimalField(max_digits=9, decimal_places=2)
    max_contig_length = models.PositiveIntegerField()

    n50_contig_length = models.PositiveIntegerField()
    l50_contig_count = models.PositiveSmallIntegerField()
    ng50_contig_length = models.PositiveIntegerField()
    lg50_contig_count = models.PositiveSmallIntegerField()

    contigs_greater_1k = models.PositiveSmallIntegerField()
    contigs_greater_10k = models.PositiveSmallIntegerField()
    contigs_greater_100k = models.PositiveSmallIntegerField()
    contigs_greater_1m = models.PositiveSmallIntegerField()

    percent_contigs_greater_1k = models.DecimalField(max_digits=4,
                                                     decimal_places=2)
    percent_contigs_greater_10k = models.DecimalField(max_digits=4,
                                                      decimal_places=2)
    percent_contigs_greater_100k = models.DecimalField(max_digits=4,
                                                       decimal_places=2)
    percent_contigs_greater_1m = models.DecimalField(max_digits=4,
                                                     decimal_places=2)

    contig_percent_a = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_t = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_g = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_c = models.DecimalField(max_digits=4, decimal_places=2)
    contig_percent_n = models.DecimalField(max_digits=4, decimal_places=2)
    contig_non_acgtn = models.DecimalField(max_digits=4, decimal_places=2)
    num_contig_non_acgtn = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('sample', 'is_scaffolds', 'version')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    def pipeline_version(self):
        """ Display pipeline version in admin view. """
        return self.version.version
    pipeline_version.short_description = 'Pipeline Version'
    pipeline_version.admin_order_field = 'version'


class Kmer(models.Model):

    """ A linking table for Sample and Kmers. """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sample', 'version')


class KmerString(models.Model):

    """ Unique 31-mer strings. """

    string = models.CharField(default='', max_length=31, unique=True,
                              db_index=True)


class KmerCount(models.Model):

    """ Kmer counts from each sample. """

    kmer = models.ForeignKey('Kmer', on_delete=models.CASCADE)
    string = models.ForeignKey('KmerString', on_delete=models.CASCADE)
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('kmer', 'string')


class KmerTotal(models.Model):

    """ Total kmer counts from each sample. """

    kmer = models.ForeignKey('Kmer', on_delete=models.CASCADE)
    total = models.PositiveIntegerField()


class Variant(models.Model):

    """ A linking table for Sample and Variant. """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sample', 'version')


class VariantToIndel(models.Model):

    """ A linking table between samples and InDels. """

    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    indel = models.ForeignKey('VariantIndel', on_delete=models.CASCADE)
    info = models.ForeignKey('VariantInfo', on_delete=models.CASCADE)
    filters = models.ForeignKey('VariantFilter', on_delete=models.CASCADE)
    quality = models.DecimalField(max_digits=8, decimal_places=3)


class VariantIndel(models.Model):

    """ Information unique to the SNP. """

    reference = models.ForeignKey('VariantReference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('VariantAnnotation',
                                   on_delete=models.CASCADE)

    reference_position = models.PositiveIntegerField()
    reference_base = models.TextField()
    alternate_base = models.TextField()

    class Meta:
        unique_together = ('reference', 'reference_position', 'reference_base',
                           'alternate_base')


class VariantToSNP(models.Model):

    """ A linking table between samples and SNPs. """

    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    snp = models.ForeignKey('VariantSNP', on_delete=models.CASCADE)
    comment = models.ForeignKey('VariantComment', on_delete=models.CASCADE)
    info = models.ForeignKey('VariantInfo', on_delete=models.CASCADE)
    filters = models.ForeignKey('VariantFilter', on_delete=models.CASCADE)
    quality = models.DecimalField(max_digits=8, decimal_places=3)


class VariantComment(models.Model):

    """ SNP related comments. """

    comment = models.TextField(db_index=True, unique=True)


class VariantInfo(models.Model):

    """ All the data stored in the INFO column of the VCF. """

    AC = models.TextField()
    AD = models.TextField()
    AF = models.DecimalField(max_digits=8, decimal_places=3)
    AN = models.PositiveIntegerField()
    DP = models.PositiveIntegerField()
    GQ = models.PositiveIntegerField()
    GT = models.TextField()
    MQ = models.DecimalField(max_digits=8, decimal_places=3)
    PL = models.TextField()
    QD = models.DecimalField(max_digits=8, decimal_places=3)


class VariantFilter(models.Model):

    """ Filters that may have been applied by GATK. """

    name = models.TextField(db_index=True, unique=True)


class VariantSNP(models.Model):

    """ Information unique to the SNP. """

    reference = models.ForeignKey('VariantReference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('VariantAnnotation',
                                   on_delete=models.CASCADE)

    reference_position = models.PositiveIntegerField()
    reference_base = models.CharField(max_length=1)
    alternate_base = models.CharField(max_length=1)

    reference_codon = models.CharField(max_length=3)
    alternate_codon = models.CharField(max_length=3)

    reference_amino_acid = models.CharField(max_length=1)
    alternate_amino_acid = models.CharField(max_length=1)

    codon_position = models.PositiveIntegerField()
    snp_codon_position = models.PositiveSmallIntegerField()
    amino_acid_change = models.TextField()

    is_synonymous = models.PositiveSmallIntegerField()
    is_transition = models.PositiveSmallIntegerField()
    is_genic = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('reference', 'reference_position', 'reference_base',
                           'alternate_base')


class VariantReference(models.Model):

    """ Reference genome used for SNP calling. """

    name = models.TextField(db_index=True, unique=True)


class VariantAnnotation(models.Model):

    """ GenBank annotations of a reference genome. """

    reference = models.ForeignKey('VariantReference', on_delete=models.CASCADE)
    locus_tag = models.CharField(max_length=24)
    protein_id = models.CharField(max_length=24)
    gene = models.CharField(max_length=12)
    db_xref = models.TextField()
    product = models.TextField()
    note = models.TextField()
