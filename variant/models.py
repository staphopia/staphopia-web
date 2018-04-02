"""
Variant Application Models.

These are models to import VCF files from the Staphopia variant analysis
pipeline.
"""
import os

from django.db import models
from django.contrib.postgres.fields import JSONField

from sample.models import Sample
from version.models import Version


class Variant(models.Model):
    """A linking table between samples and InDels."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='toindel_version')
    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    snp_count = models.PositiveIntegerField(default=0)
    indel_count = models.PositiveIntegerField(default=0)
    snp = JSONField()
    indel = JSONField()

    class Meta:
        unique_together = ('sample', 'version', 'reference')


class Indel(models.Model):
    """Information unique to the SNP."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)

    reference_position = models.PositiveIntegerField(db_index=True)
    reference_base = models.TextField()
    alternate_base = models.TextField()
    is_deletion = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('reference', 'reference_position', 'reference_base',
                           'alternate_base')

    def locus_tag(self):
        """Display locus_tag in admin view."""
        return self.annotation.locus_tag
    locus_tag.short_description = 'Locus Tag'
    locus_tag.admin_order_field = 'annotation'

    def reference_strain(self):
        """Display reference name in admin view."""
        fasta = os.path.basename(self.reference.name).upper()
        return fasta.replace('.FASTA', '')
    reference_strain.short_description = 'Reference Strain'
    reference_strain.admin_order_field = 'reference'


class IndelMember(models.Model):
    """Indels and which public samples they are found in."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    indel = models.OneToOneField('Indel', on_delete=models.CASCADE)
    count = models.PositiveIntegerField(db_index=True)
    members = JSONField(default=[])

    class Meta:
        unique_together = ('reference', 'indel')


class SNP(models.Model):
    """Information unique to the SNP."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    feature = models.ForeignKey('Feature', on_delete=models.CASCADE)

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
        """Display locus_tag in admin view."""
        return self.annotation.locus_tag
    locus_tag.short_description = 'Locus Tag'
    locus_tag.admin_order_field = 'annotation'

    def reference_strain(self):
        """Display reference name in admin view."""
        fasta = os.path.basename(self.reference.name).upper()
        return fasta.replace('.FASTA', '')
    reference_strain.short_description = 'Reference Strain'
    reference_strain.admin_order_field = 'reference'


class SNPMember(models.Model):
    """SNPs and which public samples they are found in."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    snp = models.OneToOneField('SNP', on_delete=models.CASCADE)
    count = models.PositiveIntegerField(db_index=True)
    members = JSONField(default=[])

    class Meta:
        unique_together = ('reference', 'snp')


class Counts(models.Model):
    """Variant counts across all samples for quick reference."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    annotation = models.ForeignKey('Annotation', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(db_index=True)
    is_mlst_set = models.BooleanField(default=False, db_index=True)
    nongenic_indel = models.PositiveIntegerField()
    nongenic_snp = models.PositiveIntegerField()
    indel = models.PositiveIntegerField()
    synonymous = models.PositiveIntegerField()
    nonsynonymous = models.PositiveIntegerField()
    total = models.PositiveIntegerField()

    class Meta:
        unique_together = ('reference', 'position', 'is_mlst_set')


class Comment(models.Model):
    """SNP related comments."""

    comment = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """Display comment in admin view."""
        return u"%s" % self.comment


class Filter(models.Model):
    """Filters that may have been applied by GATK."""

    name = models.TextField(db_index=True, unique=True)

    def __unicode__(self):
        """Display filter name in admin view."""
        return u"%s" % self.name


class Reference(models.Model):
    """Reference used for SNP calling."""

    name = models.TextField(db_index=True, unique=True)
    length = models.PositiveIntegerField(default=0)
    sequence = models.TextField(default="")

    def __unicode__(self):
        """Display reference name in admin view."""
        return u"%s" % self.name


class ReferenceGenome(models.Model):
    """Reference genome used for SNP calling."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    sequence = JSONField()


class Feature(models.Model):
    """Genbank feature type for quick sorting of SNP/InDel Tables."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    feature = models.TextField()


class Annotation(models.Model):
    """GenBank annotations of a reference genome."""

    reference = models.ForeignKey('Reference', on_delete=models.CASCADE)
    locus_tag = models.CharField(max_length=24)
    protein_id = models.CharField(max_length=24, default="not_applicable")
    gene = models.CharField(max_length=12)
    product = models.TextField()
    note = models.TextField()
    is_pseudo = models.PositiveSmallIntegerField()
    start = models.PositiveIntegerField(default=0)
    end = models.PositiveIntegerField(default=0)
    strand = models.SmallIntegerField(default=0)

    def fixed_note(self):
        """Display note with appropriate replacements in admin view."""
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
        """Display product with appropriate replacements in admin view."""
        return self.product.replace(
            '[space]', ' '
        ).replace(
            '[semi-colon]', ';'
        ).replace(
            '[comma]', ','
        )
    fixed_product.short_description = 'Product'
    fixed_product.admin_order_field = 'product'
