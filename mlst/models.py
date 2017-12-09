"""
MLST Application Models.

These are models to store information on the MLST calls for Staphopia samples.
"""
from django.db import models

from sample.models import Sample


class SequenceTypes(models.Model):
    """Sequence type mappings from MLST database."""

    st = models.PositiveIntegerField(unique=True)
    arcc = models.PositiveIntegerField()
    aroe = models.PositiveIntegerField()
    glpf = models.PositiveIntegerField()
    gmk = models.PositiveIntegerField()
    pta = models.PositiveIntegerField()
    tpi = models.PositiveIntegerField()
    yqil = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now=True)


class Blast(models.Model):
    """Blast results from contigs against MLST loci."""

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
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
        unique_together = ('sample', 'locus_name', 'locus_id')

    def sample_tag(self):
        """Display sample tag in admin view."""
        return self.sample.sample_tag
    sample_tag.short_description = 'Sample Tag'
    sample_tag.admin_order_field = 'mlst'
