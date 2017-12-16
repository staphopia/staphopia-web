"""
SCCmec Application Models.

These are models to store information on the SCCmec related results.
"""
from django.db import models

from assembly.models import Contig
from sample.models import Sample
from staphopia.models import BlastQuery
from version.models import Version


class Cassette(models.Model):
    """Basic info for each SCCmec cassette."""

    name = models.TextField()
    header = models.TextField()
    length = models.PositiveIntegerField()
    meca_start = models.PositiveIntegerField(default=0)
    meca_stop = models.PositiveIntegerField(default=0)
    meca_length = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('name', 'header')


class Coverage(models.Model):
    """Coverage statistics for each SCCmec cassette."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE,
                               related_name='sccmec_coverage_sample')
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='sccmec_coverage_version')
    cassette = models.ForeignKey('Cassette', on_delete=models.CASCADE)

    total = models.DecimalField(max_digits=7, decimal_places=2)

    minimum = models.PositiveIntegerField()
    mean = models.DecimalField(max_digits=7, decimal_places=2)
    median = models.PositiveIntegerField()
    maximum = models.PositiveIntegerField()

    meca_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    meca_minimum = models.PositiveIntegerField(default=0)
    meca_mean = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    meca_median = models.PositiveIntegerField(default=0)
    meca_maximum = models.PositiveIntegerField(default=0)
    per_base_coverage = models.TextField()

    def sample_tag(self):
        """Display sample tag in admin view."""
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'sample'

    class Meta:
        unique_together = ('sample', 'version', 'cassette')


class Primers(models.Model):
    """BLAST hits against SCCmec primers."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='sccmec_primers_version')
    contig = models.ForeignKey(Contig, on_delete=models.CASCADE)

    query = models.ForeignKey(BlastQuery, on_delete=models.CASCADE)

    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()

    class Meta:
        unique_together = ('sample', 'version', 'query')


class Subtypes(models.Model):
    """BLAST hits against SCCmec subtype primers."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='sccmec_subtypes_version')
    contig = models.ForeignKey(Contig, on_delete=models.CASCADE)

    query = models.ForeignKey(BlastQuery, on_delete=models.CASCADE)

    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()

    class Meta:
        unique_together = ('sample', 'version', 'query')


class Proteins(models.Model):
    """BLAST hits against SCCmec proteins."""
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE,
                                related_name='sccmec_proteins_version')
    contig = models.ForeignKey(Contig, on_delete=models.CASCADE)

    query = models.ForeignKey(BlastQuery, on_delete=models.CASCADE)

    bitscore = models.PositiveSmallIntegerField()
    evalue = models.DecimalField(max_digits=7, decimal_places=2)
    identity = models.PositiveSmallIntegerField()
    mismatch = models.PositiveSmallIntegerField()
    gaps = models.PositiveSmallIntegerField()
    hamming_distance = models.PositiveSmallIntegerField()
    query_from = models.PositiveSmallIntegerField()
    query_to = models.PositiveSmallIntegerField()
    hit_from = models.PositiveIntegerField()
    hit_to = models.PositiveIntegerField()
    align_len = models.PositiveSmallIntegerField()

    qseq = models.TextField()
    hseq = models.TextField()
    midline = models.TextField()

    class Meta:
        unique_together = ('sample', 'version', 'query')
