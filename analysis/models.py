""" Table models for analysis results. """
import os
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

    n50_contig_length = models.PositiveIntegerField(default=0)
    l50_contig_count = models.PositiveSmallIntegerField(default=0)
    ng50_contig_length = models.PositiveIntegerField(default=0)
    lg50_contig_count = models.PositiveSmallIntegerField(default=0)

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


class Variant(models.Model):

    """ A linking table for Sample and Variant. """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sample', 'version')

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


class VariantToIndel(models.Model):

    """ A linking table between samples and InDels. """

    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    indel = models.ForeignKey('VariantIndel', on_delete=models.CASCADE)
    filters = models.ForeignKey('VariantFilter', on_delete=models.CASCADE)

    """ INFO and Qual, fields specific to each variant. """
    AC = models.TextField(default="")
    AD = models.TextField(default="")
    AF = models.DecimalField(default=0.0, max_digits=8, decimal_places=3)
    DP = models.PositiveIntegerField(default=0)
    GQ = models.PositiveIntegerField(default=0)
    GT = models.TextField(default="")
    MQ = models.DecimalField(default=0.0, max_digits=8, decimal_places=3)
    PL = models.TextField(default="")
    QD = models.DecimalField(default=0.0, max_digits=8, decimal_places=3)
    quality = models.DecimalField(max_digits=8, decimal_places=3)

    class Meta:
        unique_together = ('variant', 'indel')

    def variant_id(self):
        """ Display variant id in admin view. """
        return self.variant.pk
    variant_id.short_description = 'Variant ID'
    variant_id.admin_order_field = 'variant'

    def indel_id(self):
        """ Display InDel id in admin view. """
        return self.indel.pk
    indel_id.short_description = 'InDel ID'
    indel_id.admin_order_field = 'indel'


class VariantIndel(models.Model):

    """ Information unique to the SNP. """

    reference = models.ForeignKey('VariantReference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('VariantAnnotation',
                                   on_delete=models.CASCADE)

    reference_position = models.PositiveIntegerField(db_index=True)
    reference_base = models.TextField()
    alternate_base = models.TextField()
    is_deletion = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('reference', 'reference_position', 'reference_base',
                           'alternate_base')

    def locus_tag(self):
        """ Display locus_tag in admin view. """
        return self.annotation.locus_tag
    locus_tag.short_description = 'Locus Tag'
    locus_tag.admin_order_field = 'annotation'

    def reference_strain(self):
        """ Display reference name in admin view. """
        fasta = os.path.basename(self.reference.name).upper()
        return fasta.replace('.FASTA', '')
    reference_strain.short_description = 'Reference Strain'
    reference_strain.admin_order_field = 'reference'


class VariantToSNP(models.Model):

    """ A linking table between samples and SNPs. """

    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    snp = models.ForeignKey('VariantSNP', on_delete=models.CASCADE)
    comment = models.ForeignKey('VariantComment', on_delete=models.CASCADE)
    filters = models.ForeignKey('VariantFilter', on_delete=models.CASCADE)

    """ INFO and Qual, fields specific to each variant. """
    AC = models.TextField(default="")
    AD = models.TextField(default="")
    AF = models.DecimalField(default=0.0, max_digits=8, decimal_places=3)
    DP = models.PositiveIntegerField(default=0)
    GQ = models.PositiveIntegerField(default=0)
    GT = models.TextField(default="")
    MQ = models.DecimalField(default=0.0, max_digits=8, decimal_places=3)
    PL = models.TextField(default="")
    QD = models.DecimalField(default=0.0, max_digits=8, decimal_places=3)
    quality = models.DecimalField(max_digits=8, decimal_places=3)

    class Meta:
        unique_together = ('variant', 'snp')

    def sample_tag(self):
        """ Display sample_tag in admin view. """
        return self.variant.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'variant'

    def variant_id(self):
        """ Display variant id in admin view. """
        return self.variant.pk
    variant_id.short_description = 'Variant ID'
    variant_id.admin_order_field = 'variant'

    def snp_id(self):
        """ Display InDel id in admin view. """
        return self.snp.pk
    snp_id.short_description = 'SNP ID'
    snp_id.admin_order_field = 'snp'

    def snp_count(self):
        """ Display snp_counts in admin view. """
        return self.objects.filter(variant=self.variant).count()
    snp_count.short_description = 'SNP Count'


class VariantComment(models.Model):

    """ SNP related comments. """

    comment = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """ Display comment in admin view. """
        return u"%s" % self.comment


class VariantFilter(models.Model):

    """ Filters that may have been applied by GATK. """

    name = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """ Display filter name in admin view. """
        return u"%s" % self.name


class VariantSNP(models.Model):

    """ Information unique to the SNP. """

    reference = models.ForeignKey('VariantReference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('VariantAnnotation',
                                   on_delete=models.CASCADE)

    reference_position = models.PositiveIntegerField(db_index=True)
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

    def locus_tag(self):
        """ Display locus_tag in admin view. """
        return self.annotation.locus_tag
    locus_tag.short_description = 'Locus Tag'
    locus_tag.admin_order_field = 'annotation'

    def reference_strain(self):
        """ Display reference name in admin view. """
        fasta = os.path.basename(self.reference.name).upper()
        return fasta.replace('.FASTA', '')
    reference_strain.short_description = 'Reference Strain'
    reference_strain.admin_order_field = 'reference'


class VariantReference(models.Model):

    """ Reference genome used for SNP calling. """

    name = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """ Display reference name in admin view. """
        return u"%s" % self.name


class VariantAnnotation(models.Model):

    """ GenBank annotations of a reference genome. """

    reference = models.ForeignKey('VariantReference', on_delete=models.CASCADE)
    locus_tag = models.CharField(max_length=24)
    protein_id = models.CharField(max_length=24)
    gene = models.CharField(max_length=12)
    db_xref = models.TextField()
    product = models.TextField()
    note = models.TextField()

    def fixed_note(self):
        """ Display note with appropriate replacements in admin view. """
        return self.note.replace(
            '[space]', ' '
        ).replace(
            '[semi-colon]', ';'
        ).replace(
            '[comma]', ','
        )
    fixed_note.short_description = 'Note'
    fixed_note.admin_order_field = 'note'

    def fixed_product(self):
        """ Display product with appropriate replacements in admin view. """
        return self.product.replace(
            '[space]', ' '
        ).replace(
            '[semi-colon]', ';'
        ).replace(
            '[comma]', ','
        )
    fixed_product.short_description = 'Product'
    fixed_product.admin_order_field = 'product'


class MLST(models.Model):

    """ MLST results from the analysis pipeline. """

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey('PipelineVersion', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sample', 'version')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'

    def pipeline_version(self):
        """ Display pipeline version in admin view. """
        return self.version.version
    pipeline_version.short_description = 'Pipeline Version'
    pipeline_version.admin_order_field = 'version'


class MLSTSequenceType(models.Model):

    """ Sequence type mappings from MLST database. """

    ST = models.PositiveIntegerField(db_index=True, unique=True)
    arcc = models.PositiveIntegerField()
    aroe = models.PositiveIntegerField()
    glpf = models.PositiveIntegerField()
    gmk = models.PositiveIntegerField()
    pta = models.PositiveIntegerField()
    tpi = models.PositiveIntegerField()
    yqil = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)


class MLSTBlast(models.Model):

    """ Blast results from contigs against MLST loci. """

    mlst = models.ForeignKey('MLST', on_delete=models.CASCADE)
    locus_name = models.CharField(max_length=4)
    locus_id = models.PositiveSmallIntegerField()
    bitscore = models.PositiveSmallIntegerField()
    slen = models.PositiveSmallIntegerField()
    length = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    pident = models.DecimalField(max_digits=5, decimal_places=2)
    evalue = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        unique_together = ('mlst', 'locus_name', 'locus_id')

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.mlst.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'


class MLSTSrst2(models.Model):

    """ SRST2 results from mapping of FASTQ files. """

    mlst = models.ForeignKey('MLST', on_delete=models.CASCADE)
    ST = models.TextField()
    arcc = models.TextField()
    aroe = models.TextField()
    glpf = models.TextField()
    gmk = models.TextField()
    pta = models.TextField()
    tpi = models.TextField()
    yqil = models.TextField()
    mismatches = models.TextField()
    uncertainty = models.TextField()
    depth = models.DecimalField(max_digits=8, decimal_places=3)
    maxMAF = models.DecimalField(max_digits=11, decimal_places=7)

    def sample_tag(self):
        """ Display sample tag in admin view. """
        return self.mlst.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'
