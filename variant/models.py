"""
Variant Application Models.

These are models to import VCF files from the Staphopia variant analysis
pipeline.
"""

import os

from django.db import models

from analysis.models import PipelineVersion
from samples.models import Sample


class Variant(models.Model):

    """ A linking table for Sample and Variant. """

    sample = models.ForeignKey(Sample, related_name="variant_sample_id",
                               on_delete=models.CASCADE)
    version = models.ForeignKey(PipelineVersion,
                                related_name="variant_version_id",
                                on_delete=models.CASCADE)

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


class ToIndel(models.Model):

    """ A linking table between samples and InDels. """

    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    indel = models.ForeignKey('Indel', on_delete=models.CASCADE)
    filters = models.ForeignKey('Filter', on_delete=models.CASCADE)
    confidence = models.ForeignKey('Confidence', on_delete=models.CASCADE)

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


class Indel(models.Model):

    """ Information unique to the SNP. """

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)

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


class ToSNP(models.Model):

    """ A linking table between samples and SNPs. """

    variant = models.ForeignKey('Variant', on_delete=models.CASCADE)
    snp = models.ForeignKey('SNP', on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    confidence = models.ForeignKey('Confidence', on_delete=models.CASCADE)
    filters = models.ForeignKey('Filter', on_delete=models.CASCADE)

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


class SNP(models.Model):

    """ Information unique to the SNP. """

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)

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


class Confidence(models.Model):
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


class Comment(models.Model):

    """ SNP related comments. """

    comment = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """ Display comment in admin view. """
        return u"%s" % self.comment


class Filter(models.Model):

    """ Filters that may have been applied by GATK. """

    name = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """ Display filter name in admin view. """
        return u"%s" % self.name


class Reference(models.Model):

    """ Reference genome used for SNP calling. """

    name = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """ Display reference name in admin view. """
        return u"%s" % self.name


class Annotation(models.Model):

    """ GenBank annotations of a reference genome. """

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)

    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    is_positive = models.BooleanField()

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
